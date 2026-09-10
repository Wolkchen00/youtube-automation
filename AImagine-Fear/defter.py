"""Yayin defteri (yayin.jsonl) okuma yardimcilari.

Tek kaynak: hem `tools/gunluk.py` hem `tools/yayinla.py` buradan okur. Ayrisirlarsa
donusum bir seyi "kullanilmis" sayarken ayni-gun kapisi baska bir sey sayar.

TEMEL KURAL: bir satirin VARLIGI yayin kaniti DEGILDIR. `yayinla.py` kaydi
basarisiz donmeden ONCE de yaziyor, yani basarisiz bir deneme de defterde satir
birakiyor. Kanit, YouTube yanitindan cikarilabilen bir yayin kimligidir.
"""
from __future__ import annotations

from typing import Any


# Upload-Post yaniti ic ice: results.youtube.results.youtube.post_id
# Alan adi saglayiciya gore degisebildigi icin birkac ad kabul ediliyor.
KIMLIK_ADLARI = ("post_id", "publication_id", "video_id", "id")


def yayin_kimligi(youtube_sonucu: Any) -> str | None:
    """YouTube yanitindan gercek yayin kimligini cikar, yoksa None.

    `success: true` tek basina YETMEZ: kimliksiz bir 200 yaniti yayin kaniti
    degildir ve rotayi ilerletmemelidir.
    """
    if not isinstance(youtube_sonucu, dict):
        return None
    if youtube_sonucu.get("hata"):
        return None

    def _ara(dugum: Any, derinlik: int = 0) -> str | None:
        if derinlik > 6 or not isinstance(dugum, dict):
            return None
        if dugum.get("success") is False:
            return None
        for ad in KIMLIK_ADLARI:
            deger = dugum.get(ad)
            if isinstance(deger, str) and deger.strip():
                return deger.strip()
        for anahtar in ("results", "youtube", "data", "result"):
            bulunan = _ara(dugum.get(anahtar), derinlik + 1)
            if bulunan:
                return bulunan
        return None

    return _ara(youtube_sonucu)


def kullanildi_mi(kayit: dict) -> bool:
    """Bu defter satiri DOGRULANMIS bir YouTube yayini mi?

    Yeni satirlar `kullanildi` alanini tasir. Eski satirlarda o alan YOK; onlar
    icin YouTube sonucundan cikarim yapilir. Geriye donuk dosya YAZIMI yok,
    yalnizca okuma uyumu , yoksa yeni okuyucu butun gecmisi "basarisiz" sayar,
    donusum sifirlanir ve eski basliklar yeniden secilir.
    """
    if not isinstance(kayit, dict):
        return False
    if "kullanildi" in kayit:
        return bool(kayit["kullanildi"])
    sonuclar = kayit.get("results")
    if not isinstance(sonuclar, dict):
        return False
    return yayin_kimligi(sonuclar.get("youtube")) is not None


def basarili_kayitlar(gecmis: list[dict]) -> list[dict]:
    return [kayit for kayit in gecmis if kullanildi_mi(kayit)]


def bugunku_basarili(gecmis: list[dict], bugun: str) -> list[dict]:
    """Bugun DOGRULANMIS yayin yapilmis satirlar.

    Basarisiz denemeler ayni-gun kapisini tetiklemez; yoksa sabah patlayan bir
    kosu gunun geri kalanini kilitler.
    """
    return [
        kayit
        for kayit in basarili_kayitlar(gecmis)
        if str(kayit.get("ts", "")).startswith(bugun)
    ]
