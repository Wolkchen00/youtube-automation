"""ROCK D0: kuresel Kie bakiye tabani ve sahip etiketli rezervasyonlar.

Neden var: bolum defteri de deney defteri de YALNIZ kendi kutusunu bilir. Ortak Kie
bakiyesini bes proje paylasiyor; bir workflow otekinin kredisini sessizce yiyebilir.
Bu modul ucretli cagri yapan iki kapiya (series/credit_gate.py ve series/experiment.py)
ortak bir taban koyar:

    taze bakiye - bu cagrinin tahmini - BASKASINA ait acik rezervasyonlar >= taban

Kural detaylari:
  * Bakiye ONBELLEKSIZ okunur (yetkilendirme aninda). Onbellekli bakiye, iki koşunun
    ayni krediyi harcamasina izin verir.
  * Kontrol ve rezervasyon yazimi TEK kilit altinda atomiktir; yarista yalniz biri gecer.
  * Sahip etiketli rezervasyon (ornegin kill-gate) sahibi icin HARCANABILIR bakiyedir,
    baskalari icin ise erisilemez: taban yalniz rezervasyonun DISINDAKI bakiyeyi korur.
    Boylece taban ne kill-gate'i bloke eder ne de korumasini kaybeder.
  * Taban tanimli DEGILSE (KIE_BALANCE_FLOOR yok ya da 0) modul hicbir sey yapmaz ve
    bakiye sorgusu bile atilmaz: opt-in olmayan seriler icin davranis bit-degismezdir (P9).
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from core.config import logger

STATE_PATH = Path(__file__).resolve().parents[1] / "kie_reservations.json"
LOCK_PATH = STATE_PATH.with_suffix(".lock")
LOCK_TIMEOUT_S = 30.0
LOCK_STALE_S = 120.0
INFLIGHT_TTL_S = 900.0   # yetkilendirilip henuz uzlastirilmamis cagrinin korunma suresi


class BalanceFloorError(RuntimeError):
    """Taban mekanizmasi calistirilamadi; fail-closed davranilir."""


def floor_value() -> float | None:
    """KIE_BALANCE_FLOOR degeri; tanimsiz/0/gecersiz ise kapali (None)."""
    raw = os.environ.get("KIE_BALANCE_FLOOR")
    if raw is None or str(raw).strip() == "":
        return None
    try:
        value = float(str(raw).strip())
    except (TypeError, ValueError):
        logger.warning(f"⚠️ KIE_BALANCE_FLOOR sayiya cevrilemedi: {raw!r} ,  taban kapali")
        return None
    if value <= 0:
        return None
    return value


def _lock_path(path: Path | None) -> Path:
    """Her defterin KENDI kilidi olur; testler gercek kilidi kirletmez."""
    base = Path(path) if path is not None else STATE_PATH
    return base.with_suffix(".lock")


class _FileLock:
    """Workflow'lar arasi kilit: O_EXCL + bayat kilit kurtarmasi (Windows/Linux)."""

    def __init__(self, path: Path | None = None, timeout: float = LOCK_TIMEOUT_S):
        self.path = Path(path) if path is not None else LOCK_PATH
        self.timeout = float(timeout)
        self._fd = None

    def __enter__(self):
        deadline = time.monotonic() + self.timeout
        self.path.parent.mkdir(parents=True, exist_ok=True)
        while True:
            try:
                self._fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self._fd, str(os.getpid()).encode("ascii"))
                return self
            except FileExistsError:
                try:
                    age = time.time() - self.path.stat().st_mtime
                except OSError:
                    age = 0.0
                if age > LOCK_STALE_S:
                    logger.warning("⚠️ Bayat bakiye kilidi kaldiriliyor")
                    try:
                        self.path.unlink()
                    except OSError:
                        pass
                    continue
                if time.monotonic() >= deadline:
                    raise BalanceFloorError("bakiye kilidi zaman asimina ugradi")
                time.sleep(0.05)

    def __exit__(self, *exc):
        if self._fd is not None:
            try:
                os.close(self._fd)
            finally:
                self._fd = None
        try:
            self.path.unlink()
        except OSError:
            pass
        return False


def _load(path: Path | None = None) -> dict:
    path = Path(path) if path is not None else STATE_PATH
    if not Path(path).exists():
        return {"reservations": []}
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        # Bozuk defter fail-closed FATAL durumdur (credits_ledger dersi): bos defterle
        # degistirip fail-open kalmak, korumayi sessizce kapatir.
        raise BalanceFloorError(f"rezervasyon defteri okunamadi: {error}") from error
    if not isinstance(data, dict) or not isinstance(data.get("reservations"), list):
        raise BalanceFloorError("rezervasyon defteri bicimi gecersiz")
    return data


def _save(data: dict, path: Path | None = None) -> None:
    path = Path(path) if path is not None else STATE_PATH
    tmp = Path(path).with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _expired(reservation: dict, now: float | None = None) -> bool:
    """Uzlastirilmadan kalan ucusta kaydi, TTL sonunda korumayi birakir."""
    expires = reservation.get("expires_at")
    if expires is None:
        return False
    return float(expires) <= (time.time() if now is None else now)


def _remaining(reservation: dict, now: float | None = None) -> float:
    if _expired(reservation, now):
        return 0.0
    return max(0.0, float(reservation.get("amount", 0)) - float(reservation.get("spent", 0)))


def outstanding(exclude_owner: str | None = None, *, path: Path | None = None) -> float:
    """Acik (harcanmamis) rezervasyon toplami; exclude_owner disarida birakilir."""
    data = _load(path)
    return sum(
        _remaining(r) for r in data["reservations"]
        if exclude_owner is None or r.get("owner") != exclude_owner
    )


def reserve(owner: str, amount: float, *, note: str = "", path: Path | None = None) -> str:
    """Sahip etiketli rezervasyon ac; dondurulen id ile harcanir/serbest birakilir."""
    if not owner or float(amount) <= 0:
        raise ValueError("rezervasyon icin sahip ve pozitif miktar zorunlu")
    with _FileLock(_lock_path(path)):
        data = _load(path)
        reservation_id = uuid.uuid4().hex
        data["reservations"].append({
            "id": reservation_id,
            "owner": str(owner),
            "amount": float(amount),
            "spent": 0.0,
            "note": str(note),
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
        _save(data, path)
    logger.info(f"🔒 Kredi rezervasyonu acildi: {owner} {float(amount):g} kr ({reservation_id[:8]})")
    return reservation_id


def release(reservation_id: str, *, path: Path | None = None) -> bool:
    """Rezervasyonu kapat (kalan koruma serbest kalir)."""
    with _FileLock(_lock_path(path)):
        data = _load(path)
        before = len(data["reservations"])
        data["reservations"] = [r for r in data["reservations"] if r.get("id") != reservation_id]
        changed = len(data["reservations"]) != before
        if changed:
            _save(data, path)
    return changed


@dataclass
class FloorDecision:
    allowed: bool
    reason: str = ""
    balance: float | None = None
    floor: float | None = None
    outstanding_others: float = 0.0
    owner_allowance: float = 0.0
    consumed: float = 0.0
    inflight_id: str | None = None


def authorize_spend(estimate: float, *, owner: str | None = None,
                    balance_checker=None, path: Path | None = None) -> FloorDecision:
    """Tabani gozeterek ucretli cagriyi yetkilendir (ve sahip rezervasyonundan dus).

    Taban kapaliysa hicbir sey yapmaz ve bakiye SORGULANMAZ.
    """
    floor = floor_value()
    if floor is None:
        return FloorDecision(True, "taban kapali")
    if balance_checker is None:
        from core.kie_api import check_credit as balance_checker  # gec import: test kolayligi
    try:
        estimate = float(estimate)
    except (TypeError, ValueError):
        return FloorDecision(False, "tahmin sayiya cevrilemedi", floor=floor)

    with _FileLock(_lock_path(path)):
        data = _load(path)
        balance = balance_checker()
        if balance is None:
            # Bakiye olculemiyorsa fail-closed: koruma varsayimla calistirilmaz.
            return FloorDecision(False, "canli bakiye okunamadi", floor=floor)
        balance = float(balance)
        # Ucusta para HERKES icin dusulur: yetkilendirilmis ama daha bakiyeden
        # inmemis harcamadir; sahibi kim olursa olsun tekrar harcanamaz.
        committed = sum(
            _remaining(r) for r in data["reservations"] if r.get("kind") == "inflight"
        )
        held = [r for r in data["reservations"] if r.get("kind") != "inflight"]
        own_list = [r for r in held if owner is not None and r.get("owner") == owner]
        others = sum(
            _remaining(r) for r in held
            if owner is None or r.get("owner") != owner
        )
        own = sum(_remaining(r) for r in own_list)
        free = balance - committed - others - floor
        allowance = own + max(0.0, free)
        if estimate > allowance:
            return FloorDecision(
                False,
                (f"taban korumasi: tahmin {estimate:g} > izin {allowance:g} "
                 f"(bakiye {balance:g}, baskasinin rezervasyonu {others:g}, "
                 f"ucusta {committed:g}, taban {floor:g})"),
                balance=balance, floor=floor, outstanding_others=others,
                owner_allowance=allowance,
            )
        # Once SAHIBIN rezervasyonundan dus: koruma tuketildikce serbest bakiyeye geciler.
        consumed = 0.0
        left = estimate
        for reservation in own_list:
            if left <= 0:
                break
            take = min(_remaining(reservation), left)
            if take <= 0:
                continue
            reservation["spent"] = float(reservation.get("spent", 0)) + take
            consumed += take
            left -= take
        inflight_id = None
        if left > 0:
            # Serbest bakiyeden harcanan kisim UCUSTA kaydi birakir: yoksa iki
            # esszamanli cagri ayni krediyi gorup tabani birlikte delerdi.
            inflight_id = uuid.uuid4().hex
            data["reservations"].append({
                "id": inflight_id,
                "owner": owner,
                "kind": "inflight",
                "amount": float(left),
                "spent": 0.0,
                "expires_at": time.time() + INFLIGHT_TTL_S,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            })
        if consumed or inflight_id:
            _save(data, path)
        return FloorDecision(
            True, "", balance=balance, floor=floor, outstanding_others=others,
            owner_allowance=allowance, consumed=consumed, inflight_id=inflight_id,
        )


def settle(reservation_owner: str | None, estimate: float, actual: float | None, *,
           inflight_id: str | None = None, path: Path | None = None) -> None:
    """Cagri bittiginde ucusta kaydini kapat ve harcanmayan tahmini geri ver."""
    if inflight_id:
        release(inflight_id, path=path)
    if reservation_owner is None or actual is None:
        return
    try:
        delta = float(estimate) - float(actual)
    except (TypeError, ValueError):
        return
    if delta <= 0:
        return
    with _FileLock(_lock_path(path)):
        data = _load(path)
        for reservation in data["reservations"]:
            if reservation.get("owner") != reservation_owner:
                continue
            spent = float(reservation.get("spent", 0))
            if spent <= 0:
                continue
            give_back = min(spent, delta)
            reservation["spent"] = spent - give_back
            delta -= give_back
            if delta <= 0:
                break
        _save(data, path)
