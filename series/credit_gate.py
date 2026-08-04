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


logger = logging.getLogger("credit_gate")

_ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER_PATH = _ROOT / "credits_ledger.json"

_EPISODE_DEFAULT = 900
_MONTHLY_DEFAULT = 20000


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
        if type(entry.get("reserved")) is not int:
            raise ValueError("reserved alanı geçersiz")
        if entry.get("actual") is not None and type(entry.get("actual")) is not int:
            raise ValueError("actual alanı geçersiz")
        if not isinstance(entry.get("ts"), str):
            raise ValueError("ts alanı geçersiz")
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
    """Bozuk defteri kopyala ve ana defteri boş bir yapıyla yenile."""
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
    _save(_empty_ledger())


def _load() -> dict:
    """Defteri oku; eksik dosyayı boş, bozuk dosyayı kenara alınmış say."""
    path = pathlib.Path(LEDGER_PATH)
    if not path.exists():
        return _empty_ledger()
    raw = path.read_bytes()
    try:
        return _validate(json.loads(raw.decode("utf-8")))
    except Exception as error:
        _shelve_corrupt(raw, error)
        return _empty_ledger()


def month_total(month: str) -> int:
    """Ay için gerçek harcamaları, yoksa rezervasyonları topla."""
    total = 0
    for entry in _load()["entries"]:
        if entry["month"] == month:
            actual = entry["actual"]
            total += actual if actual is not None else entry["reserved"]
    return total


def reserve(series: str, part: int) -> bool:
    """Bölüm kredisini aylık defterde ayır; tavan aşılıyorsa False döndür."""
    data = _load()
    month = _current_month()
    used = sum(
        entry["actual"] if entry["actual"] is not None else entry["reserved"]
        for entry in data["entries"]
        if entry["month"] == month
    )
    amount = episode_cap()
    limit = monthly_cap()
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


def reconcile(series: str, part: int, actual: int | None) -> None:
    """En yeni açık rezervasyonu gerçek harcamayla uzlaştır.

    actual None ise rezervasyon tam olarak ayakta kalır. Eşleşen açık kayıt yoksa
    savunmacı olarak uzlaştırılmış yeni bir kayıt eklenir.
    """
    data = _load()
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
            "reserved": episode_cap(),
            "actual": actual,
            "ts": _timestamp(),
        }
        entries.append(match)
        logger.warning(
            "Açık rezervasyon bulunamadı; savunmacı kayıt eklendi: seri=%s part=%s",
            series, part,
        )
    elif actual is not None:
        match["actual"] = int(actual)
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


def run_gate(balance: int | None) -> bool:
    """Başlangıç bakiyesi güvenli eşiği karşılıyorsa True döndür."""
    threshold = episode_cap() * 1.5
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

    @property
    def blocked(self) -> bool:
        return self.blocked_reason is not None

    @property
    def remaining(self) -> float | None:
        if self.spent is None:
            return None
        return max(0.0, float(self.cap) - float(self.spent))

    @property
    def last_estimate(self) -> float | None:
        return self.reservations[-1]["estimate"] if self.reservations else None

    def authorize(self, call_type: str, engine: str, duration=None) -> bool:
        """Reserve the next call's estimate; unknown/over-cap calls are blocked."""
        from core.cost_tracker import conservative_credit_estimate

        estimate = conservative_credit_estimate(call_type, engine, duration)
        if self.spent is None:
            self.blocked_reason = "mevcut bölüm harcaması okunamadı"
        elif estimate is None:
            self.blocked_reason = (
                f"bilinmeyen maliyet: çağrı={call_type}, motor={engine}, süre={duration}"
            )
        elif float(self.spent) + float(estimate) > float(self.cap):
            self.blocked_reason = (
                f"sert tavan aşımı: harcanan={float(self.spent):g}, "
                f"sonraki={float(estimate):g}, tavan={float(self.cap):g}"
            )
        else:
            self.spent = float(self.spent) + float(estimate)
            self.reservations.append({
                "call_type": call_type,
                "engine": engine,
                "duration": None if duration is None else str(duration),
                "estimate": float(estimate),
            })
            return True
        logger.error("Kredi sert tavanı çağrıyı engelledi: %s", self.blocked_reason)
        return False
