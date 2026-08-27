"""Kie harcamaları için bölüm ve aylık kredi korumaları.

Rezervasyon, üretim başlamadan önce kalıcı deftere yazılır. Üretim sonunda
bilinen gerçek harcama ile uzlaştırılır; bilinmeyen harcama rezervasyonu korur.
"""

import datetime
import json
import logging
import os
from dataclasses import dataclass, field
import pathlib
import time
from numbers import Real


logger = logging.getLogger("credit_gate")

_ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER_PATH = _ROOT / "credits_ledger.json"

_EPISODE_DEFAULT = 900
_MONTHLY_DEFAULT = 20000


class LedgerCorruptError(RuntimeError):
    """Raised when the durable paid-call ledger cannot be trusted."""


def _env_int(name: str, default: int) -> int:
    """Boş veya geçersiz ortam değerinde güvenli varsayılanı döndür."""
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        logger.error("%s tam sayı değil (%r); varsayılan %s kullanılıyor",
                     name, raw, default)
        return default


def episode_cap() -> int:
    """Bölüm başına kredi tavanını döndür."""
    return _env_int("EPISODE_CREDIT_CAP", _EPISODE_DEFAULT)


def monthly_cap() -> int:
    """Aylık kredi tavanını döndür."""
    return _env_int("MONTHLY_CREDIT_CAP", _MONTHLY_DEFAULT)


def _current_month() -> str:
    """UTC takvimine göre geçerli ayı YYYY-MM biçiminde döndür."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m")


def _timestamp() -> str:
    """Defter kaydı için UTC ISO zaman damgası üret."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _empty_ledger() -> dict:
    """Boş defter yapısını döndür."""
    # Keep the legacy on-disk shape until durable per-episode accounting is
    # explicitly used by an opted-in series.
    return {"entries": []}


def _validate(data: object) -> dict:
    """Defter şemasını doğrula; bozuk veride hata yükselt."""
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        raise ValueError("defter kökünde entries listesi yok")
    for entry in data["entries"]:
        if not isinstance(entry, dict):
            raise ValueError("defter girdisi nesne değil")
        if not isinstance(entry.get("month"), str):
            raise ValueError("month alanı geçersiz")
        if not isinstance(entry.get("series"), str):
            raise ValueError("series alanı geçersiz")
        if type(entry.get("part")) is not int:
            raise ValueError("part alanı geçersiz")
        if type(entry.get("reserved")) is not int or entry["reserved"] < 0:
            raise ValueError("reserved alanı geçersiz")
        if (entry.get("actual") is not None
                and (isinstance(entry.get("actual"), bool)
                     or not isinstance(entry.get("actual"), Real)
                     or float(entry["actual"]) < 0)):
            raise ValueError("actual alanı geçersiz")
        if not isinstance(entry.get("ts"), str):
            raise ValueError("ts alanı geçersiz")
    spends = data.get("episode_spend", {})
    if not isinstance(spends, dict):
        raise ValueError("episode_spend alanı nesne değil")
    for key, value in spends.items():
        if (not isinstance(key, str) or not key
                or isinstance(value, bool) or not isinstance(value, Real)
                or float(value) < 0):
            raise ValueError("episode_spend girdisi geçersiz")
    return data


def _save(data: dict) -> None:
    """Defteri geçici dosya ve atomik değiştirme ile kalıcı yaz."""
    path = pathlib.Path(LEDGER_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(
        f"{path.name}.tmp-{os.getpid()}-{time.time_ns()}"
    )
    try:
        temp_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _shelve_corrupt(raw: bytes, error: Exception) -> None:
    """Best-effort forensic copy; the corrupt authoritative file stays untouched."""
    path = pathlib.Path(LEDGER_PATH)
    stamp = int(time.time())
    aside = path.with_name(f"credits_ledger.corrupt-{stamp}.json")
    while aside.exists():
        stamp += 1
        aside = path.with_name(f"credits_ledger.corrupt-{stamp}.json")
    logger.error("Kredi defteri bozuk: %s. Kopya: %s", error, aside)
    try:
        aside.write_bytes(raw)
    except Exception:
        logger.exception("Bozuk kredi defteri kopyalanamadı; ana dosya korunuyor")
        raise


def _load() -> dict:
    """Read the ledger; corruption is fatal and never becomes an empty ledger."""
    path = pathlib.Path(LEDGER_PATH)
    if not path.exists():
        return _empty_ledger()
    raw = path.read_bytes()
    try:
        return _validate(json.loads(raw.decode("utf-8")))
    except Exception as error:
        try:
            _shelve_corrupt(raw, error)
        except Exception:
            pass
        raise LedgerCorruptError(f"kredi defteri bozuk: {error}") from error


def month_total(month: str) -> int | None:
    """Ay için gerçek harcamaları, yoksa rezervasyonları topla."""
    total = 0
    try:
        entries = _load()["entries"]
    except LedgerCorruptError as error:
        logger.error("Aylık toplam okunamadı; ücretli çağrılar kapalı: %s", error)
        return None
    for entry in entries:
        if entry["month"] == month:
            actual = entry["actual"]
            total += actual if actual is not None else entry["reserved"]
    return total


def _episode_key(series: str, part: int) -> str:
    return f"{series}:{int(part)}"


def _episode_spent_from(data: dict, series: str, part: int) -> float:
    key = _episode_key(series, part)
    spends = data.get("episode_spend") or {}
    if key in spends:
        return float(spends[key])
    return float(sum(
        entry["actual"] or 0
        for entry in data["entries"]
        if entry["series"] == series and entry["part"] == int(part)
        and entry["actual"] is not None
    ))


def episode_spent(series: str, part: int) -> float | None:
    """Return durable cumulative actuals for one series part."""
    try:
        return _episode_spent_from(_load(), series, part)
    except LedgerCorruptError as error:
        logger.error("Bölüm harcaması okunamadı; ücretli çağrılar kapalı: %s", error)
        return None


def record_episode_spend(series: str, part: int, amount: float) -> bool:
    """Atomically add one paid call's actual (or conservative fallback) charge."""
    if isinstance(amount, bool) or not isinstance(amount, Real) or float(amount) < 0:
        logger.error("Geçersiz bölüm harcaması: %r", amount)
        return False
    try:
        data = _load()
    except LedgerCorruptError as error:
        logger.error("Harcama yazılamadı; ücretli çağrılar kapalı: %s", error)
        return False
    key = _episode_key(series, part)
    current = _episode_spent_from(data, series, part)
    data.setdefault("episode_spend", {})[key] = current + float(amount)
    try:
        _save(data)
    except OSError as error:
        logger.error("Kalıcı bölüm harcaması yazılamadı: %s", error)
        return False
    return True


def ledger_healthy() -> bool:
    try:
        _load()
        return True
    except LedgerCorruptError as error:
        logger.error("Kredi defteri FATAL: %s", error)
        return False


def reserve(series: str, part: int, *, cap: int | None = None,
            resume_episode: bool = False,
            monthly_limit: int | None = None) -> bool:
    """Bölüm kredisini aylık defterde ayır; tavan aşılıyorsa False döndür."""
    try:
        data = _load()
    except LedgerCorruptError as error:
        logger.error("Rezervasyon reddedildi; kredi defteri FATAL: %s", error)
        return False
    month = _current_month()
    configured_cap = int(cap if cap is not None else episode_cap())
    spent = _episode_spent_from(data, series, part) if resume_episode else 0.0
    amount = max(0, int(configured_cap - spent)) if resume_episode else configured_cap
    if amount <= 0:
        logger.error(
            "Bölüm kredi tavanı dolu: seri=%s part=%s harcanan=%s tavan=%s",
            series, part, spent, configured_cap,
        )
        return False
    if resume_episode:
        open_entries = [
            entry for entry in data["entries"]
            if entry["series"] == series and entry["part"] == int(part)
            and entry["actual"] is None
        ]
        same_month = next(
            (entry for entry in reversed(open_entries) if entry["month"] == month), None
        )
        if same_month is not None:
            same_month["reserved"] = min(int(same_month["reserved"]), configured_cap)
            _save(data)
            logger.info(
                "Mevcut bölüm rezervasyonu sürdürüldü: seri=%s part=%s kalan=%s",
                series, part, amount,
            )
            return True
        if open_entries:
            prior_actual = sum(
                float(entry["actual"] or 0) for entry in data["entries"]
                if entry["series"] == series and entry["part"] == int(part)
                and entry["actual"] is not None
            )
            open_entries[-1]["actual"] = max(0.0, float(spent) - prior_actual)
    scoped_monthly = monthly_limit is not None
    used = sum(
        entry["actual"] if entry["actual"] is not None else entry["reserved"]
        for entry in data["entries"]
        if entry["month"] == month
        and (not scoped_monthly or entry["series"] == series)
    )
    limit = int(monthly_limit if monthly_limit is not None else monthly_cap())
    if used + amount > limit:
        logger.error(
            "Aylık kredi tavanı: ay=%s mevcut=%s bölüm=%s tavan=%s; rezervasyon reddedildi",
            month, used, amount, limit,
        )
        return False
    data["entries"].append({
        "month": month,
        "series": series,
        "part": int(part),
        "reserved": amount,
        "actual": None,
        "ts": _timestamp(),
    })
    _save(data)
    logger.info(
        "Kredi rezerve edildi: seri=%s part=%s miktar=%s ay_toplamı=%s",
        series, part, amount, used + amount,
    )
    return True


def reconcile(series: str, part: int, actual: int | float | None,
              *, cap: int | None = None) -> bool:
    """En yeni açık rezervasyonu gerçek harcamayla uzlaştır.

    actual None ise rezervasyon tam olarak ayakta kalır. Eşleşen açık kayıt yoksa
    savunmacı olarak uzlaştırılmış yeni bir kayıt eklenir.
    """
    try:
        data = _load()
    except LedgerCorruptError as error:
        logger.error("Uzlaştırma yapılamadı; kredi defteri FATAL: %s", error)
        return False
    entries = data["entries"]
    match = None
    for entry in reversed(entries):
        if (entry["series"] == series and entry["part"] == int(part)
                and entry["actual"] is None):
            match = entry
            break
    if match is None:
        match = {
            "month": _current_month(),
            "series": series,
            "part": int(part),
            "reserved": int(cap if cap is not None else episode_cap()),
            "actual": actual,
            "ts": _timestamp(),
        }
        entries.append(match)
        logger.warning(
            "Açık rezervasyon bulunamadı; savunmacı kayıt eklendi: seri=%s part=%s",
            series, part,
        )
    elif actual is not None:
        prior = sum(
            float(entry["actual"] or 0)
            for entry in entries
            if entry is not match and entry["series"] == series
            and entry["part"] == int(part) and entry["actual"] is not None
        )
        match["actual"] = max(0, float(actual) - prior)
    _save(data)
    if actual is None:
        logger.warning(
            "Gerçek harcama bilinmiyor; rezervasyon korunuyor: seri=%s part=%s",
            series, part,
        )
    else:
        logger.info(
            "Kredi uzlaştırıldı: seri=%s part=%s gerçek=%s",
            series, part, actual,
        )
    return True


def run_gate(balance: int | None, *, cap: int | None = None) -> bool:
    """Başlangıç bakiyesi güvenli eşiği karşılıyorsa True döndür."""
    threshold = int(cap if cap is not None else episode_cap()) * 1.5
    if balance is None:
        logger.error("Kie bakiyesi okunamadı; üretim güvenli şekilde durduruldu")
        return False
    if balance < threshold:
        logger.error(
            "Kie bakiyesi yetersiz: bakiye=%s eşik=%s",
            balance, threshold,
        )
        return False
    return True


@dataclass
class HardCreditCap:
    """Opt-in, per-episode pre-spend budget using conservative estimates."""

    cap: float
    spent: float | None = 0.0
    blocked_reason: str | None = None
    reservations: list[dict] = field(default_factory=list)
    durable_ledger: bool = False
    balance_owner: str | None = None   # ROCK D0: kuresel taban icin sahip etiketi

    @property
    def blocked(self) -> bool:
        return self.blocked_reason is not None

    @property
    def remaining(self) -> float | None:
        if self.blocked:
            return None
        if self.durable_ledger and not ledger_healthy():
            return None
        if self.spent is None:
            return None
        return max(0.0, float(self.cap) - float(self.spent))

    @property
    def last_estimate(self) -> float | None:
        return self.reservations[-1]["estimate"] if self.reservations else None

    def settle_last(self, actual: float | int | None) -> bool:
        """Replace the latest conservative reservation with a measured charge."""
        if actual is None:
            return True
        if (isinstance(actual, bool) or not isinstance(actual, Real)
                or float(actual) < 0 or not self.reservations or self.spent is None):
            self.blocked_reason = "gerçek kredi uzlaştırması geçersiz"
            logger.error("Kredi sert tavanı uzlaştırması başarısız: %r", actual)
            return False
        reservation = self.reservations[-1]
        if reservation.get("settled"):
            self.blocked_reason = "aynı kredi rezervasyonu iki kez uzlaştırıldı"
            logger.error("Kredi sert tavanı uzlaştırması iki kez çağrıldı")
            return False
        estimate = float(reservation["estimate"])
        self.spent = float(self.spent) - estimate + float(actual)
        reservation["actual"] = float(actual)
        reservation["settled"] = True
        # ROCK D0: ucusta tutulan koruma birakilir, harcanmayan tahmin sahibin
        # rezervasyonuna geri doner. Yapilmazsa taban kendi filosunu bogar.
        if reservation.get("floor_inflight_id") or self.balance_owner:
            from series import balance_floor
            try:
                balance_floor.settle(
                    self.balance_owner, estimate, float(actual),
                    inflight_id=reservation.get("floor_inflight_id"),
                )
            except balance_floor.BalanceFloorError as error:
                logger.warning("Kredi tabani uzlastirmasi yapilamadi: %s", error)
        if float(self.spent) > float(self.cap):
            self.blocked_reason = (
                f"gerçek harcama sert tavanı aştı: harcanan={float(self.spent):g}, "
                f"tavan={float(self.cap):g}"
            )
            logger.error("Kredi sert tavanı gerçek harcamada aşıldı: %s", self.blocked_reason)
            return False
        return True

    def authorize(self, call_type: str, engine: str, duration=None,
                  optional: bool = False) -> bool:
        """Sonraki çağrıyı rezerve et; isteğe bağlı ret sert tavanı zehirlemez."""
        from core.cost_tracker import conservative_credit_estimate

        estimate = conservative_credit_estimate(call_type, engine, duration)
        if self.blocked:
            reason = self.blocked_reason or "kredi sert tavanı önceden kapandı"
        elif self.durable_ledger and not ledger_healthy():
            reason = "kalıcı kredi defteri bozuk veya okunamıyor"
        elif self.spent is None:
            reason = "mevcut bölüm harcaması okunamadı"
        elif estimate is None:
            reason = (
                f"bilinmeyen maliyet: çağrı={call_type}, motor={engine}, süre={duration}"
            )
        elif float(self.spent) + float(estimate) > float(self.cap):
            reason = (
                f"sert tavan aşımı: harcanan={float(self.spent):g}, "
                f"sonraki={float(estimate):g}, tavan={float(self.cap):g}"
            )
        else:
            # ROCK D0: yerel tavan gecti; simdi ORTAK bakiye tabani. Taban kapaliysa
            # bu cagri hicbir sey yapmaz ve bakiye bile sorgulanmaz (P9).
            from series import balance_floor
            try:
                decision = balance_floor.authorize_spend(
                    float(estimate), owner=self.balance_owner
                )
            except balance_floor.BalanceFloorError as error:
                decision = balance_floor.FloorDecision(False, f"taban mekanizmasi: {error}")
            if not decision.allowed:
                reason = f"ortak bakiye tabani: {decision.reason}"
                if optional:
                    logger.warning("Kredi tabani istege bagli cagriyi reddetti: %s", reason)
                    return False
                self.blocked_reason = reason
                logger.error("Kredi tabani cagriyi engelledi: %s", reason)
                return False
            self.spent = float(self.spent) + float(estimate)
            self.reservations.append({
                "call_type": call_type,
                "engine": engine,
                "duration": None if duration is None else str(duration),
                "estimate": float(estimate),
                "floor_inflight_id": decision.inflight_id,
            })
            return True
        if optional:
            logger.warning("Kredi sert tavanı isteğe bağlı çağrıyı reddetti: %s", reason)
            return False
        self.blocked_reason = reason
        logger.error("Kredi sert tavanı çağrıyı engelledi: %s", self.blocked_reason)
        return False


@dataclass
class CompositeCreditCap:
    """Require two independent authorizers for every paid call.

    The episode cap remains the source of estimates and allocator state.  The
    second authorizer is normally an experiment gate backed by its own durable
    ledger.  If the second gate refuses, the in-memory episode reservation is
    settled to zero because no provider call was made.
    """

    episode_cap: HardCreditCap
    experiment_gate: object
    blocked_reason: str | None = None

    @property
    def cap(self) -> float:
        return self.episode_cap.cap

    @property
    def spent(self) -> float | None:
        return self.episode_cap.spent

    @property
    def reservations(self) -> list[dict]:
        return self.episode_cap.reservations

    @property
    def blocked(self) -> bool:
        return bool(
            self.blocked_reason
            or self.episode_cap.blocked
            or getattr(self.experiment_gate, "blocked", False)
        )

    @property
    def remaining(self) -> float | None:
        episode_remaining = self.episode_cap.remaining
        experiment_remaining = getattr(self.experiment_gate, "remaining", None)
        if episode_remaining is None or experiment_remaining is None:
            return None
        return min(float(episode_remaining), float(experiment_remaining))

    @property
    def last_estimate(self) -> float | None:
        return self.episode_cap.last_estimate

    def authorize(self, call_type: str, engine: str, duration=None,
                  optional: bool = False) -> bool:
        if self.blocked and not optional:
            logger.error(
                "Birleşik kredi kapısı önceden kapandı: %s",
                self.blocked_reason or "alt kapılardan biri kapalı",
            )
            return False
        if not self.episode_cap.authorize(
            call_type, engine, duration, optional=optional
        ):
            if not optional:
                self.blocked_reason = (
                    self.episode_cap.blocked_reason or "bölüm kredi kapısı reddetti"
                )
            return False
        try:
            allowed = self.experiment_gate.authorize(
                call_type, engine, duration, optional=optional
            )
        except TypeError:
            # A simple authorizer only needs the three-argument protocol.
            allowed = self.experiment_gate.authorize(call_type, engine, duration)
        if allowed:
            return True

        # No paid call happened. Release only the just-created episode estimate;
        # the durable experiment gate did not create a reservation on refusal.
        self.episode_cap.settle_last(0)
        reason = (
            getattr(self.experiment_gate, "blocked_reason", None)
            or "deney kredi kapısı reddetti"
        )
        if not optional:
            self.blocked_reason = reason
            logger.error("Birleşik kredi kapısı çağrıyı engelledi: %s", reason)
        return False

    def settle_last(self, actual: float | int | None) -> bool:
        episode_ok = self.episode_cap.settle_last(actual)
        experiment_ok = self.experiment_gate.settle_last(actual)
        if episode_ok and experiment_ok:
            return True
        self.blocked_reason = (
            self.episode_cap.blocked_reason
            or getattr(self.experiment_gate, "blocked_reason", None)
            or "birleşik kredi uzlaştırması başarısız"
        )
        logger.error("Birleşik kredi kapısı uzlaştırması başarısız: %s", self.blocked_reason)
        return False
