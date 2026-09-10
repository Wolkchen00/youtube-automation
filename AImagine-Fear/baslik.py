"""YouTube kanca basliklari icin saf dogrulama mantigi.

Bu modul, YouTube Shorts baslik varyantlarinin gecerliligini kontrol eder.
Dosya G/C, ag islemi veya proje iceri import yoktur; sadece Python standart
kutuphanesi (re) kullanilir.
"""

from __future__ import annotations

import re
from typing import List, Optional


def normalize(metin: str) -> str:
    """Metni kucultur, a-z ve 0-9 disi karakter dizilerini tek boslukla degistirir.

    Args:
        metin: Islenecek metin.

    Returns:
        Normalize edilmis metin (kucuk harf, alfanumerik disi tek bosluk, kenarlar
        temizlenmis).
    """
    return re.sub(r"[^a-z0-9]+", " ", metin.lower()).strip()


def dogrula_baslik(satir: str, anahtar_kelime: str) -> List[str]:
    """Tek bir baslik varyantini dogrular.

    Args:
        satir: Baslik satiri (sonundaki bosluklar atilacak).
        anahtar_kelime: Ilk 40 karakterde aranacak anahtar kelime.

    Returns:
        Sorun metinleri listesi. Bos liste gecerli demektir.
    """
    sorunlar: List[str] = []
    stripped = satir.rstrip()

    # a) "#shorts" ile bitmeli (kucuk harf, case-sensitive)
    if not stripped.endswith("#shorts"):
        sorunlar.append(f'baslik "#shorts" ile bitmiyor: {stripped!r}')

    # b) Toplam uzunluk <= 70 (dahil "#shorts")
    if len(stripped) > 70:
        sorunlar.append(f'baslik uzunlugu {len(stripped)} karakter, maksimum 70: {stripped!r}')

    # c) anahtar_kelime ilk 40 karakterde gecmeli (case-insensitive)
    if not anahtar_kelime or not anahtar_kelime.strip():
        sorunlar.append("anahtar kelime bos")
    else:
        ilk_40 = stripped[:40].lower()
        if anahtar_kelime.lower() not in ilk_40:
            sorunlar.append(f'anahtar kelime "{anahtar_kelime}" ilk 40 karakterde yok: {stripped[:40]!r}')

    # d) 40. karakter (0-based index 39 ve 40) kelime icinde olmamali
    if len(stripped) > 40:
        char_39 = stripped[39]
        char_40 = stripped[40]
        if char_39 != " " and char_40 != " ":
            sorunlar.append(f'karakter 40 kelime icinde kesiliyor: {stripped[35:45]!r}')

    return sorunlar


def varyantlar_gecerli(satirlar: List[str], anahtar_kelime: str) -> List[str]:
    """Butun baslik varyantlarini dogrular.

    Args:
        satirlar: Baslik varyantlari listesi.
        anahtar_kelime: Her varyant icin aranacak anahtar kelime.

    Returns:
        Sorun metinleri listesi. Bos liste gecerli demektir.
    """
    sorunlar: List[str] = []

    # Bos/yalniz bosluk satirlarini atla
    gecerli_satirlar = [(i + 1, s) for i, s in enumerate(satirlar) if s.strip()]

    # En az 2, en fazla 5 varyant
    sayi = len(gecerli_satirlar)
    if sayi < 2:
        sorunlar.append(f"varyant sayisi {sayi}, minimum 2 olmali")
    elif sayi > 5:
        sorunlar.append(f"varyant sayisi {sayi}, maksimum 5 olmali")

    # Her varyanti dogrula
    for idx, satir in gecerli_satirlar:
        varyant_sorunlari = dogrula_baslik(satir, anahtar_kelime)
        for s in varyant_sorunlari:
            sorunlar.append(f"varyant {idx}: {s}")

    # Normalize edilmis formlarda eslesme yok (daha kati)
    normalize_edilmis = {}
    for idx, satir in gecerli_satirlar:
        norm = normalize(satir)
        if norm in normalize_edilmis:
            onceki_idx = normalize_edilmis[norm]
            sorunlar.append(f"varyant {onceki_idx} ve varyant {idx} normalize edince ayni: {norm!r}")
        else:
            normalize_edilmis[norm] = idx

    return sorunlar


def ilk_kullanilmamis(varyantlar: List[str], kullanilmis: List[str]) -> Optional[str]:
    """Ilk kullanilmamis varyanti dondurur.

    Args:
        varyantlar: Aday varyantlar (orijinal halleriyle).
        kullanilmis: Daha once kullanilmis basliklar.

    Returns:
        Ilk kullanilmamis varyant (orijinal haliyle) veya None.
    """
    kullanilmis_norm = {normalize(k) for k in kullanilmis}

    for v in varyantlar:
        if not v.strip():
            continue
        if normalize(v) not in kullanilmis_norm:
            return v

    return None