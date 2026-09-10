"""baslik.py icin bagimsiz saldiri testleri (Claude, Level 10).

Nemotron'un yazdigi modulu kirmaya calisir. Sinir degerleri, unicode, ve
"gecmesi kolay" gorunen ama yanlis olan vakalar.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

PROJE_KOKU = Path(__file__).resolve().parent.parent
if str(PROJE_KOKU) not in sys.path:
    sys.path.insert(0, str(PROJE_KOKU))

import baslik  # noqa: E402


ANAHTAR = "Burj"


def _uzunlukta(hedef: int, anahtar: str = ANAHTAR) -> str:
    """Tam `hedef` karakter uzunlugunda, kurallara uyan bir baslik uret."""
    kuyruk = " #shorts"
    # 40. karakterin boslugа denk gelmesi icin dolgu kelimelerini ayarla
    bas = anahtar + " drop"
    dolgu_uzunluk = hedef - len(bas) - len(kuyruk)
    dolgu = " " + "x" * (dolgu_uzunluk - 1) if dolgu_uzunluk > 0 else ""
    return bas + dolgu + kuyruk


# ----------------------------------------------------------------------
# normalize: yukleyicinin formuluyle BIREBIR ayni olmali
# ----------------------------------------------------------------------
@pytest.mark.parametrize("metin", [
    "STRAT Tower Drop! #shorts",
    "",
    "!!!???",
    "Burj Khalifa 2026 #shorts",
    "emoji 🌑💦 var #shorts",
    "TURKCE İĞÜŞÇÖ karakterler",
    "  bosluklu  ",
])
def test_normalize_formule_birebir_uyuyor(metin: str) -> None:
    beklenen = re.sub(r"[^a-z0-9]+", " ", metin.lower()).strip()
    assert baslik.normalize(metin) == beklenen


def test_sadece_noktalama_bos_donuyor_ve_ikisi_ayni_sayiliyor() -> None:
    assert baslik.normalize("!!!") == ""
    assert baslik.normalize("???") == ""
    sorunlar = baslik.varyantlar_gecerli(["!!! #shorts", "??? #shorts"], ANAHTAR)
    assert any("normalize edince ayni" in s for s in sorunlar)


# ----------------------------------------------------------------------
# Uzunluk siniri: 70 GECER, 71 KALIR
# ----------------------------------------------------------------------
def test_tam_70_gecer_71_kalir() -> None:
    yetmis = _uzunlukta(70)
    assert len(yetmis) == 70
    assert not [s for s in baslik.dogrula_baslik(yetmis, ANAHTAR) if "uzunlug" in s]

    yetmisbir = _uzunlukta(71)
    assert len(yetmisbir) == 71
    assert [s for s in baslik.dogrula_baslik(yetmisbir, ANAHTAR) if "uzunlug" in s]


# ----------------------------------------------------------------------
# #shorts kurali
# ----------------------------------------------------------------------
@pytest.mark.parametrize("satir,gecmeli", [
    ("Burj drop tonight #shorts", True),
    ("Burj drop tonight #shorts   ", True),    # sondaki bosluk strip'lenir
    ("Burj drop tonight #Shorts", False),      # buyuk harf KABUL EDILMEZ
    ("Burj drop tonight #SHORTS", False),
    ("Burj drop tonight #shorts extra", False),  # sonda degil
    ("Burj drop tonight", False),              # hic yok
])
def test_shorts_etiketi_kurali(satir: str, gecmeli: bool) -> None:
    sorunlar = [s for s in baslik.dogrula_baslik(satir, ANAHTAR) if "#shorts" in s]
    assert (not sorunlar) == gecmeli


# ----------------------------------------------------------------------
# Anahtar kelime ilk 40 karakterde olmali
# ----------------------------------------------------------------------
def test_anahtar_40tan_sonra_sayilmaz() -> None:
    """Anahtar kelime satirda VAR ama kancanin disinda: gecersiz."""
    onek = "The clear glass slide high over the city "   # 41 karakter
    satir = onek + "Burj #shorts"
    assert len(onek) > 40, "test kurgusu: onek 40 karakteri asmali"
    assert satir.index("Burj") > 40
    assert "Burj" in satir, "anahtar kelime satirda olmali, sadece gec konumda"
    assert [s for s in baslik.dogrula_baslik(satir, ANAHTAR) if "anahtar kelime" in s]


def test_anahtar_buyuk_kucuk_harfe_duyarsiz() -> None:
    assert not [
        s for s in baslik.dogrula_baslik("BURJ tower drop #shorts", "burj")
        if "anahtar kelime" in s
    ]


def test_bos_anahtar_kelime_sorun() -> None:
    assert any("anahtar kelime bos" in s for s in baslik.dogrula_baslik("x #shorts", ""))
    assert any("anahtar kelime bos" in s for s in baslik.dogrula_baslik("x #shorts", "   "))


# ----------------------------------------------------------------------
# 40. karakter kelime ortasina denk gelmemeli
# ----------------------------------------------------------------------
def test_40inci_karakter_kelime_ortasinda_kalir() -> None:
    # 40. karakter uzun bir kelimenin tam ortasinda
    satir = "Burj Khalifa transparent slide aaaaaaaaaaaaaaaa drop #shorts"
    assert len(satir) > 40 and satir[39] != " " and satir[40] != " "
    assert [s for s in baslik.dogrula_baslik(satir, ANAHTAR) if "karakter 40" in s]


def test_40inci_karakter_boslukta_gecer() -> None:
    satir = "Burj Khalifa slide over Dubai tonight qq drop #shorts"
    # 39 ya da 40 boslukta olacak sekilde ayarla
    if satir[39] != " " and satir[40] != " ":
        pytest.skip("test verisi kurgusu tutmadi")
    assert not [s for s in baslik.dogrula_baslik(satir, ANAHTAR) if "karakter 40" in s]


def test_tam_40_karakterlik_satir_kural_d_den_muaf() -> None:
    satir = _uzunlukta(40)
    assert len(satir) == 40
    assert not [s for s in baslik.dogrula_baslik(satir, ANAHTAR) if "karakter 40" in s]


# ----------------------------------------------------------------------
# Varyant kumesi kurallari
# ----------------------------------------------------------------------
def test_tek_varyant_kalir_ikisi_gecer() -> None:
    tek = ["Burj drop tonight #shorts"]
    assert any("minimum 2" in s for s in baslik.varyantlar_gecerli(tek, ANAHTAR))
    iki = ["Burj drop tonight #shorts", "Burj glass fall now #shorts"]
    assert baslik.varyantlar_gecerli(iki, ANAHTAR) == []


def test_alti_varyant_kalir() -> None:
    alti = ["Burj drop %d tonight #shorts" % i for i in range(6)]
    assert any("maksimum 5" in s for s in baslik.varyantlar_gecerli(alti, ANAHTAR))


def test_bos_satirlar_sayilmaz() -> None:
    satirlar = ["", "Burj drop tonight #shorts", "   ", "Burj glass fall now #shorts", ""]
    assert baslik.varyantlar_gecerli(satirlar, ANAHTAR) == []


def test_sadece_noktalama_farki_olan_varyantlar_ayni_sayilir() -> None:
    """Yukleyici noktalama ve emojiyi atiyor: bunlar AYNI baslik."""
    satirlar = ["Burj Tower Drop! #shorts", "burj tower drop #shorts"]
    sorunlar = baslik.varyantlar_gecerli(satirlar, ANAHTAR)
    assert any("normalize edince ayni" in s for s in sorunlar), (
        "birebir farkli ama yukleyici icin AYNI olan iki varyant gecti"
    )


def test_emoji_farki_da_ayni_sayilir() -> None:
    satirlar = ["Burj tower drop 🌑 #shorts", "Burj tower drop #shorts"]
    assert any("normalize edince ayni" in s
               for s in baslik.varyantlar_gecerli(satirlar, ANAHTAR))


def test_bos_liste_ve_tamamen_bos_liste() -> None:
    assert any("minimum 2" in s for s in baslik.varyantlar_gecerli([], ANAHTAR))
    assert any("minimum 2" in s for s in baslik.varyantlar_gecerli(["", "  "], ANAHTAR))


# ----------------------------------------------------------------------
# Varyant secici
# ----------------------------------------------------------------------
def test_ilk_kullanilmamis_orijinali_dondurur() -> None:
    varyantlar = ["Burj Tower DROP! #shorts", "Burj glass fall #shorts"]
    secilen = baslik.ilk_kullanilmamis(varyantlar, [])
    assert secilen == "Burj Tower DROP! #shorts", "normalize edilmis hali donduruldu"


def test_ilk_kullanilmamis_normalize_ile_karsilastirir() -> None:
    """Defterde noktalamasiz hali varsa, noktalamalisi da KULLANILMIS sayilmali."""
    varyantlar = ["Burj Tower Drop! #shorts", "Burj glass fall #shorts"]
    kullanilmis = ["burj tower drop shorts"]
    assert baslik.ilk_kullanilmamis(varyantlar, kullanilmis) == "Burj glass fall #shorts"


def test_havuz_tukenince_none() -> None:
    varyantlar = ["Burj a #shorts", "Burj b #shorts"]
    kullanilmis = ["Burj A! #shorts", "burj b shorts"]
    assert baslik.ilk_kullanilmamis(varyantlar, kullanilmis) is None


def test_secici_bos_satirlari_atlar() -> None:
    assert baslik.ilk_kullanilmamis(["", "  ", "Burj a #shorts"], []) == "Burj a #shorts"
    assert baslik.ilk_kullanilmamis(["", "  "], []) is None
