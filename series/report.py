"""
Üretim Raporu — her çekimin Excel/CSV kaydı (İhsan'ın "anlaşılır rapor" tercihi).

Dosyalar: output/series/<slug>/series_log.csv  (+ series_log.xlsx)
CSV utf-8-sig ile yazılır → Excel Türkçe karakterleri doğru açar.
"""

import csv
from datetime import datetime
from pathlib import Path

from core.config import logger
from core.cost_tracker import DOLLAR_PER_CREDIT
from .bible import data_dir

COLUMNS = [
    "tarih", "bölüm", "çekim", "karakterler", "sesler", "süre_sn",
    "çözünürlük", "seed", "kredi", "dolar", "durum", "video_url", "yerel_dosya",
]


def csv_path(slug: str) -> Path:
    return data_dir(slug) / "series_log.csv"


def xlsx_path(slug: str) -> Path:
    return data_dir(slug) / "series_log.xlsx"


def make_row(*, episode, shot_n, characters, audio_ids, duration, resolution,
             seed, credits, status, video_url="", local_file="") -> dict:
    """Tek satırlık rapor kaydı oluştur."""
    dolar = round((credits or 0) * DOLLAR_PER_CREDIT, 3) if credits is not None else ""
    return {
        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "bölüm": episode,
        "çekim": shot_n,
        "karakterler": ", ".join(characters or []),
        "sesler": ", ".join(audio_ids or []),
        "süre_sn": duration,
        "çözünürlük": resolution,
        "seed": "" if seed is None else seed,
        "kredi": "" if credits is None else credits,
        "dolar": dolar,
        "durum": status,
        "video_url": video_url or "",
        "yerel_dosya": str(local_file) if local_file else "",
    }


def append_row(slug: str, row: dict) -> Path:
    """Rapora bir satır ekle (yoksa başlık yazar)."""
    p = csv_path(slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    exists = p.exists()
    with open(p, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        if not exists:
            w.writeheader()
        w.writerow({c: row.get(c, "") for c in COLUMNS})
    return p


def read_rows(slug: str) -> list[dict]:
    p = csv_path(slug)
    if not p.exists():
        return []
    with open(p, "r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def export_xlsx(slug: str) -> Path | None:
    """CSV'yi Excel (.xlsx) olarak da dışa aktar (openpyxl varsa)."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font
    except ImportError:
        logger.warning("⚠️ openpyxl yok — yalnızca CSV üretildi")
        return None

    rows = read_rows(slug)
    wb = Workbook()
    ws = wb.active
    ws.title = "Üretim"
    ws.append(COLUMNS)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for r in rows:
        ws.append([r.get(c, "") for c in COLUMNS])
    out = xlsx_path(slug)
    try:
        wb.save(out)
        logger.info(f"📊 Excel raporu: {out}")
        return out
    except PermissionError:
        logger.warning(f"⚠️ {out} açık olabilir — kapatıp tekrar dene")
        return None


def summarize(slug: str) -> dict:
    """Toplam kredi/dolar/çekim özetini döndür."""
    rows = read_rows(slug)
    total_credits = sum(float(r["kredi"]) for r in rows if r.get("kredi"))
    ok = sum(1 for r in rows if r.get("durum") == "ok")
    return {
        "çekim_sayısı": len(rows),
        "başarılı": ok,
        "toplam_kredi": total_credits,
        "toplam_dolar": round(total_credits * DOLLAR_PER_CREDIT, 2),
    }
