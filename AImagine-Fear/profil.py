"""AImagine-Fear uretim profili, yetenek matrisi ve uretim kaydi yardimcilari."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


KOK = Path(__file__).resolve().parent
# 720p, cunku 1080p ayni 15 sn'lik videoyu 2,5 kat pahaliya uretiyor. Kie'nin
# kendi faturasi (recordInfo creditsConsumed), ayni model/sure/ses:
#   720p  615 kredi ($3,08)  taskId 7e4efdeddb311cc4f1fd210535d68471
#   1080p 1530 kredi ($7,65) taskId 311e039faf7db184311c7d1d0ed47717
# 2026-09-10'da maliyet olculmeden 1080p yapildi, 11 Eylul'de olculunce Ihsan
# geri aldirdi. 1080p'ye donmek Ihsan'in karari; burayi sessizce degistirme.
VARSAYILAN_PROFIL = "720p"

PROFILLER = {
    "1080p": {
        "cozunurluk": "1080p",
        "genislik": 1080,
        "yukseklik": 1920,
        "beklenen_fps": 24,
        "fps_tolerans": 0.1,
        "sure_tolerans": 1.5,
        "min_bayt": 3_000_000,
    },
    "720p": {
        "cozunurluk": "720p",
        "genislik": 720,
        "yukseklik": 1280,
        "beklenen_fps": 24,
        "fps_tolerans": 0.1,
        "sure_tolerans": 1.5,
        "min_bayt": 3_000_000,
    },
}


def matris_anahtari(
    model: str, sure: int | float, cozunurluk: str, fps: int | float
) -> tuple[str, int | float, str, int | float]:
    """Yetenek matrisinin tek kanonik anahtar ureticisi."""
    sure_sayi = float(sure)
    fps_sayi = float(fps)
    sure_kanonik = int(sure_sayi) if sure_sayi.is_integer() else sure_sayi
    fps_kanonik = int(fps_sayi) if fps_sayi.is_integer() else fps_sayi
    return str(model), sure_kanonik, str(cozunurluk), fps_kanonik


# core/kie_api.py:489'daki "4-15s / 480p-720p" notu seedance-2-fast'e
# aittir; burada kullanilan fast OLMAYAN seedance-2 modeline ait degildir.
YETENEK_MATRISI = {
    matris_anahtari("bytedance/seedance-2", 15, "720p", 24): "dogrulandi",
    matris_anahtari("bytedance/seedance-2", 15, "720p", 30): "kanarya",
    matris_anahtari("bytedance/seedance-2", 15, "1080p", 24): "kanarya",
}


def profil_hash(path: str | Path | None = None) -> str:
    """Profil kaynak kodunu satir sonundan bagimsiz SHA-256 ile damgala."""
    kaynak = Path(path) if path is not None else Path(__file__)
    metin = kaynak.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(metin).hexdigest()


def uretim_kaydi_bul(
    master_sha: str, kok: str | Path | None = None
) -> dict | None:
    """Master SHA'sina ait degismez uretim kaydini bul ve dogrula."""
    proje = Path(kok) if kok is not None else KOK
    yollar = list((proje / "out").glob(f"*/uretim/{master_sha}.json"))
    if len(yollar) != 1:
        return None
    try:
        kayit = json.loads(yollar[0].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None
    if not isinstance(kayit, dict) or kayit.get("master_sha") != master_sha:
        return None
    return kayit
