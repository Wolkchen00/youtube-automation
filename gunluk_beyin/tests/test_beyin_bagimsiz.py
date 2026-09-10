# -*- coding: utf-8 -*-
"""
Bagimsiz (dusmanca) test paketi: `python beyin.py beyin <kanal>`

Bu dosya beyin.py'nin ICINE BAKMADAN, sadece davranis sozlesmesine gore yazildi.
Amac kodu kirmak: sinir vakalari (n=14 / n=15), bozuk veri, None degerler,
sifira bolme, unicode, asiri buyuk/sifir degerler.

Calistirma:
    pytest test_beyin_bagimsiz.py -v

beyin.py'yi bulma sirasi:
    1) BEYIN_PY ortam degiskeni (dosya yolu)
    2) cwd ve ustundeki klasorlerde beyin.py
    3) bu test dosyasinin klasoru ve ustleri
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------- kesif

ZAMAN_ASIMI = 90  # saniye


def _beyin_py_bul():
    ortam = os.environ.get("BEYIN_PY", "").strip()
    if ortam:
        p = Path(ortam).expanduser()
        if p.is_file():
            return p.resolve()
    adaylar = []
    burada = Path.cwd().resolve()
    adaylar.append(burada)
    adaylar.extend(burada.parents)
    testin_yeri = Path(__file__).resolve().parent
    adaylar.append(testin_yeri)
    adaylar.extend(testin_yeri.parents)
    gorulen = set()
    for klasor in adaylar:
        if klasor in gorulen:
            continue
        gorulen.add(klasor)
        aday = klasor / "beyin.py"
        if aday.is_file():
            return aday.resolve()
    return None


BEYIN_PY = _beyin_py_bul()

gerekli = pytest.mark.skipif(
    BEYIN_PY is None,
    reason="beyin.py bulunamadi. BEYIN_PY=<yol> ortam degiskeniyle yolunu ver "
           "ya da testi proje kokunden calistir.",
)

# ------------------------------------------------------- sozlesme sabitleri

BASLIKLAR = [
    "## 1. DURUM",
    "## 2. BU KANALDA NE ISE YARIYOR",
    "## 3. GENEL ESIKLER",
    "## 4. BUGUN ICIN YON",
    "## 5. KACIN",
]

YETERSIZ = "YETERSIZ VERI"

# n < 15 iken 2. ve 4. bolumde bulunmamasi gereken "sayisal karsilastirma iddiasi"
# kaliplari. Sozlesme: o kanala ozel hicbir sayisal karsilastirma iddiasi olmamali.
KARSILASTIRMA_KALIPLARI = [
    r"\d+\s*%",
    r"%\s*\d+",
    r"\bkat\s+(daha|fazla|iyi)\b",
    r"\bvs\b",
    r"daha\s+(fazla|iyi|cok|az)\s+izlen",
    r"ortalama\s+izlen",
    r"\bmedyan\b",
    r"\bkorelasyon\b",
    r"ust\s*yari|alt\s*yari",
    r"en\s+iyi\s+\d+",
]

# ---------------------------------------------------------------- yardimcilar


def _normalize(metin: str) -> str:
    """Turkce ozel harfleri ASCII'ye indirger ve buyuk harfe cevirir."""
    cevrim = str.maketrans(
        "İıŞşĞğÜüÖöÇç",
        "IiSsGgUuOoCc",
    )
    return metin.translate(cevrim).upper()


def yetersiz_gecer(metin: str) -> bool:
    """Turkce varyantlari da yakalayan gevsek 'YETERSIZ VERI' kontrolu."""
    return YETERSIZ in _normalize(metin)


def kayit(i: int = 0, **ust) -> dict:
    """Sozlesmedeki sekle uygun tek bir defter kaydi uretir."""
    olcum_ust = ust.pop("olcum", None)
    sonuc_ust = ust.pop("sonuc", None)

    kayit_ = {
        "video_id": "vid%03d" % i,
        "kanal": "ornek",
        "tarih": "2026-09-%02d" % ((i % 28) + 1),
        "baslik": "Baslik %d" % i,
        "olcum": {
            "cozunurluk": "1080x1920",
            "fps": 30.0,
            "sure": 15.1 + (i % 5),
            "lufs": -14.3 + (i % 3),
            "true_peak": -1.1,
            "lra": 5.3,
            "ses_var": True,
            "kesme_sayisi": 2 + (i % 4),
            "kesme_per_10sn": 1.3 + (i % 3) * 0.4,
            "en_uzun_plan": 8.4,
            "ort_plan": 5.0,
        },
        "kelime": 32 + i,
        "wpm": 86 + (i % 20),
        "sonuc": {"izlenme": 1000 + i * 137, "begeni": 9 + i, "gecmis": []},
        "olculdu_ts": "2026-09-10T12:00:00Z",
    }

    if olcum_ust is not None:
        if olcum_ust is _SIL:
            del kayit_["olcum"]
        elif isinstance(olcum_ust, dict):
            kayit_["olcum"].update(olcum_ust)
        else:
            kayit_["olcum"] = olcum_ust

    if sonuc_ust is not None:
        if sonuc_ust is _SIL:
            del kayit_["sonuc"]
        elif isinstance(sonuc_ust, dict):
            kayit_["sonuc"].update(sonuc_ust)
        else:
            kayit_["sonuc"] = sonuc_ust

    for anahtar, deger in ust.items():
        if deger is _SIL:
            kayit_.pop(anahtar, None)
        else:
            kayit_[anahtar] = deger
    return kayit_


class _Sil:
    """Bir alani tamamen kaldirmak icin isaretci."""

    def __repr__(self):
        return "<SIL>"


_SIL = _Sil()


def kayitlar(n: int, **ust) -> list:
    return [kayit(i, **ust) for i in range(n)]


def defter_yaz(kok: Path, kanal: str, satirlar, son_satir_sonu: bool = True) -> Path:
    """
    kanallar/<kanal>/defter.jsonl dosyasini yazar.
    `satirlar` icindeki dict'ler JSON'a cevrilir, str'ler HAM olarak yazilir.
    """
    hedef = kok / "kanallar" / kanal / "defter.jsonl"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    parcalar = []
    for satir in satirlar:
        if isinstance(satir, str):
            parcalar.append(satir)
        else:
            parcalar.append(json.dumps(satir, ensure_ascii=False))
    icerik = "\n".join(parcalar)
    if son_satir_sonu and icerik:
        icerik += "\n"
    with open(hedef, "w", encoding="utf-8", newline="\n") as f:
        f.write(icerik)
    return hedef


def _araci_kopyala(kok: Path) -> None:
    """beyin.py'yi (ve yanindaki ust duzey .py yardimcilarini) gecici koke kopyalar."""
    kaynak_klasor = BEYIN_PY.parent
    shutil.copy2(BEYIN_PY, kok / "beyin.py")
    for komsu in kaynak_klasor.glob("*.py"):
        if komsu.name == "beyin.py" or komsu.name.startswith("test_"):
            continue
        try:
            shutil.copy2(komsu, kok / komsu.name)
        except OSError:
            pass


def calistir(kok: Path, kanal: str, komut: str = "beyin"):
    """
    `python beyin.py <komut> <kanal>` calistirir, cwd=kok.
    Ag cagrisi yapilmadigindan emin olmak icin proxy'ler olu bir porta yonlendirilir.
    """
    _araci_kopyala(kok)
    ortam = dict(os.environ)
    ortam["PYTHONDONTWRITEBYTECODE"] = "1"
    ortam["NO_COLOR"] = "1"
    # Ag cagrisi denenirse hizlica patlasin, asilmasin:
    for anahtar in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        ortam[anahtar] = "http://127.0.0.1:9"
    ortam.pop("ALL_PROXY", None)
    ortam["NO_PROXY"] = ""

    return subprocess.run(
        [sys.executable, "beyin.py", komut, kanal],
        cwd=str(kok),
        env=ortam,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=ZAMAN_ASIMI,
    )


def beyin_yolu(kok: Path, kanal: str) -> Path:
    return kok / "kanallar" / kanal / "BEYIN.md"


def beyin_oku(kok: Path, kanal: str) -> str:
    """BEYIN.md'yi KATI utf-8 ile okur (cp1252 ile yazilmissa burada patlar)."""
    yol = beyin_yolu(kok, kanal)
    ham = yol.read_bytes()
    try:
        return ham.decode("utf-8")
    except UnicodeDecodeError as hata:
        pytest.fail("BEYIN.md utf-8 degil (muhtemelen encoding verilmeden "
                    "yazilmis): %s" % hata)


def traceback_yok(proc) -> None:
    tumu = (proc.stdout or "") + (proc.stderr or "")
    assert "Traceback (most recent call last)" not in tumu, (
        "Arac traceback dokuyor:\n" + tumu[-3000:]
    )
    for gurultu in ("JSONDecodeError", "KeyError:", "TypeError:", "ZeroDivisionError",
                    "AttributeError:", "UnicodeDecodeError", "UnicodeEncodeError"):
        assert gurultu not in tumu, (
            "Yakalanmamis istisna sizmis (%s):\n%s" % (gurultu, tumu[-3000:])
        )


def basarili_olmali(proc, kok: Path, kanal: str) -> str:
    """Gecerli veride: exit 0, BEYIN.md yazilmis, bes baslik var."""
    traceback_yok(proc)
    assert proc.returncode == 0, (
        "exit=%s beklenen 0.\nstdout:\n%s\nstderr:\n%s"
        % (proc.returncode, proc.stdout, proc.stderr)
    )
    assert beyin_yolu(kok, kanal).is_file(), "BEYIN.md yazilmadi"
    metin = beyin_oku(kok, kanal)
    baslik_kontrol(metin)
    return metin


def dayanikli_olmali(proc, kok: Path, kanal: str):
    """
    Bozuk/eksik veride: ya exit 0 + gecerli BEYIN.md, ya exit 1 + anlasilir mesaj.
    Her iki durumda da traceback YOK.
    Doner: BEYIN.md metni (varsa) yoksa None.
    """
    traceback_yok(proc)
    assert proc.returncode in (0, 1), (
        "Beklenmeyen exit kodu %s\nstdout:\n%s\nstderr:\n%s"
        % (proc.returncode, proc.stdout, proc.stderr)
    )
    if proc.returncode == 0:
        assert beyin_yolu(kok, kanal).is_file(), "exit 0 ama BEYIN.md yok"
        metin = beyin_oku(kok, kanal)
        baslik_kontrol(metin)
        bolum3_dolu_kontrol(metin)
        return metin
    mesaj = ((proc.stderr or "") + (proc.stdout or "")).strip()
    assert len(mesaj) >= 8, "exit 1 ama anlasilir bir hata mesaji yok"
    return None


def baslik_kontrol(metin: str) -> None:
    for baslik in BASLIKLAR:
        assert baslik in metin, (
            "Baslik birebir yok: %r\n--- BEYIN.md ---\n%s" % (baslik, metin[:2000])
        )


def bolum(metin: str, no: int) -> str:
    """1..5 arasi bolum govdesini dondurur (baslik satiri haric)."""
    baslik = BASLIKLAR[no - 1]
    bas = metin.find(baslik)
    assert bas != -1, "Baslik bulunamadi: %r" % baslik
    icerik_bas = bas + len(baslik)
    son = len(metin)
    for digeri in BASLIKLAR:
        yer = metin.find(digeri, icerik_bas)
        if yer != -1:
            son = min(son, yer)
    return metin[icerik_bas:son]


def dolu_satirlar(govde: str) -> list:
    return [s.strip() for s in govde.splitlines() if s.strip()]


def bolum3_dolu_kontrol(metin: str) -> None:
    govde = bolum(metin, 3)
    satirlar = dolu_satirlar(govde)
    assert satirlar, "3. bolum (GENEL ESIKLER) bos"
    duz = "".join(satirlar)
    assert len(duz) >= 20, "3. bolum fazla ciliz: %r" % govde[:300]
    assert re.search(r"\d", duz), (
        "3. bolum sayisal esik icermiyor: %r" % govde[:300]
    )
    assert not yetersiz_gecer(govde), (
        "3. bolum HER ZAMAN dolu olmali, YETERSIZ VERI yazamaz: %r" % govde[:300]
    )


@pytest.fixture()
def kok(tmp_path):
    return tmp_path


# ==================================================================== testler


def test_beyin_py_bulundu():
    """Once araci bulabildigimizden emin ol (sessiz skip tuzagina dusme)."""
    assert BEYIN_PY is not None, (
        "beyin.py bulunamadi. Proje kokunden calistir ya da BEYIN_PY=<yol> ver."
    )
    assert BEYIN_PY.is_file()


@gerekli
def test_bes_baslik_birebir_var(kok):
    defter_yaz(kok, "ornek", kayitlar(20))
    proc = calistir(kok, "ornek")
    metin = basarili_olmali(proc, kok, "ornek")
    for baslik in BASLIKLAR:
        assert metin.count(baslik) == 1, "Baslik tekrar etmis: %r" % baslik


@gerekli
def test_baslik_sirasi_dogru(kok):
    defter_yaz(kok, "ornek", kayitlar(18))
    proc = calistir(kok, "ornek")
    metin = basarili_olmali(proc, kok, "ornek")
    yerler = [metin.find(b) for b in BASLIKLAR]
    assert yerler == sorted(yerler), "Bolum sirasi bozuk: %s" % yerler


@gerekli
def test_beyin_md_dogru_yola_yazilir(kok):
    defter_yaz(kok, "kanal-2", kayitlar(16))
    proc = calistir(kok, "kanal-2")
    basarili_olmali(proc, kok, "kanal-2")
    assert (kok / "kanallar" / "kanal-2" / "BEYIN.md").is_file()
    # yanlis yerlere yazmasin
    assert not (kok / "BEYIN.md").exists()
    assert not (kok / "kanallar" / "BEYIN.md").exists()


# ------------------------------------------------ ZORUNLU DURUSTLUK: SINIRLAR


@gerekli
def test_n14_yetersiz_veri_bolum_2_ve_4(kok):
    """SINIR: n=14 yetersiz. 2. ve 4. bolum YETERSIZ VERI ICERMELI."""
    defter_yaz(kok, "az", kayitlar(14))
    proc = calistir(kok, "az")
    metin = basarili_olmali(proc, kok, "az")
    b2 = bolum(metin, 2)
    b4 = bolum(metin, 4)
    assert YETERSIZ in b2, "n=14 iken 2. bolumde 'YETERSIZ VERI' yok:\n%r" % b2[:600]
    assert YETERSIZ in b4, "n=14 iken 4. bolumde 'YETERSIZ VERI' yok:\n%r" % b4[:600]
    bolum3_dolu_kontrol(metin)


@gerekli
def test_n14_sayisal_karsilastirma_iddiasi_yok(kok):
    """n=14 iken 2. ve 4. bolumde kanala ozel sayisal karsilastirma iddiasi OLMAMALI."""
    defter_yaz(kok, "az", kayitlar(14))
    proc = calistir(kok, "az")
    metin = basarili_olmali(proc, kok, "az")
    for no in (2, 4):
        govde = bolum(metin, no)
        for kalip in KARSILASTIRMA_KALIPLARI:
            eslesme = re.search(kalip, govde, re.IGNORECASE)
            assert eslesme is None, (
                "n=14 iken %d. bolumde yasak karsilastirma iddiasi var "
                "(kalip=%r, eslesen=%r):\n%s"
                % (no, kalip, eslesme.group(0), govde[:600])
            )


@gerekli
@pytest.mark.parametrize("n", [0, 1, 2, 7, 13, 14])
def test_15ten_az_hep_yetersiz(kok, n):
    """Sinirin altindaki HER n icin durustluk kurali gecerli."""
    defter_yaz(kok, "az", kayitlar(n))
    proc = calistir(kok, "az")
    metin = dayanikli_olmali(proc, kok, "az")
    if metin is None:
        return  # anlasilir hata ile cikmis, kabul
    assert yetersiz_gecer(bolum(metin, 2)), (
        "n=%d iken 2. bolum yetersiz veri demiyor" % n
    )
    assert yetersiz_gecer(bolum(metin, 4)), (
        "n=%d iken 4. bolum yetersiz veri demiyor" % n
    )


@gerekli
def test_n15_yetersiz_veri_yok(kok):
    """SINIR: n=15 yeterli. 2. bolum YETERSIZ VERI ICERMEMELI."""
    defter_yaz(kok, "tam", kayitlar(15))
    proc = calistir(kok, "tam")
    metin = basarili_olmali(proc, kok, "tam")
    b2 = bolum(metin, 2)
    assert not yetersiz_gecer(b2), (
        "n=15 (sinir) iken 2. bolum hala 'YETERSIZ VERI' diyor:\n%s" % b2[:600]
    )


@gerekli
def test_n15_karsilastirma_satirlari_var(kok):
    """n=15 iken 2. bolum gercek karsilastirma satirlari icermeli, bos gecmemeli."""
    defter_yaz(kok, "tam", kayitlar(15))
    proc = calistir(kok, "tam")
    metin = basarili_olmali(proc, kok, "tam")
    b2 = bolum(metin, 2)
    satirlar = dolu_satirlar(b2)
    assert len(satirlar) >= 2, (
        "n=15 iken 2. bolumde en az 2 karsilastirma satiri bekleniyordu:\n%r" % b2[:600]
    )
    assert any(re.search(r"\d", s) for s in satirlar), (
        "n=15 iken 2. bolumde hic sayi yok, karsilastirma yapilmamis:\n%r" % b2[:600]
    )


@gerekli
@pytest.mark.parametrize("n", [15, 16, 30])
def test_15_ve_ustu_yeterli(kok, n):
    defter_yaz(kok, "tam", kayitlar(n))
    proc = calistir(kok, "tam")
    metin = basarili_olmali(proc, kok, "tam")
    assert not yetersiz_gecer(bolum(metin, 2)), (
        "n=%d iken 2. bolum yetersiz veri diyor" % n
    )
    bolum3_dolu_kontrol(metin)


@gerekli
@pytest.mark.parametrize("n", [0, 1, 14, 15, 25])
def test_bolum3_her_zaman_dolu(kok, n):
    """3. bolum veri miktarindan BAGIMSIZ olarak hep dolu olmali."""
    defter_yaz(kok, "esik", kayitlar(n))
    proc = calistir(kok, "esik")
    metin = dayanikli_olmali(proc, kok, "esik")
    if metin is not None:
        bolum3_dolu_kontrol(metin)


# ------------------------------------------------------------- DAYANIKLILIK


@gerekli
def test_defter_dosyasi_yok(kok):
    (kok / "kanallar" / "hayalet").mkdir(parents=True, exist_ok=True)
    proc = calistir(kok, "hayalet")
    dayanikli_olmali(proc, kok, "hayalet")


@gerekli
def test_kanal_klasoru_bile_yok(kok):
    proc = calistir(kok, "hicyok")
    dayanikli_olmali(proc, kok, "hicyok")


@gerekli
def test_bos_defter_dosyasi(kok):
    defter_yaz(kok, "bos", [])
    assert (kok / "kanallar" / "bos" / "defter.jsonl").read_text() == ""
    proc = calistir(kok, "bos")
    dayanikli_olmali(proc, kok, "bos")


@gerekli
def test_sadece_bosluk_ve_bos_satirlar(kok):
    defter_yaz(kok, "bosluk", ["", "   ", "\t", ""])
    proc = calistir(kok, "bosluk")
    dayanikli_olmali(proc, kok, "bosluk")


@gerekli
def test_bozuk_json_satiri(kok):
    satirlar = []
    for i in range(5):
        satirlar.append(kayit(i))
    satirlar.append("{bu json degil")
    satirlar.append("{\"yarim\": ")
    satirlar.append("")
    satirlar.append(kayit(99))
    defter_yaz(kok, "bozuk", satirlar)
    proc = calistir(kok, "bozuk")
    dayanikli_olmali(proc, kok, "bozuk")


@gerekli
def test_bozuk_satirlar_arasinda_15_gecerli_kayit(kok):
    """Bozuk satirlar atlansa bile 15 gecerli kayit varsa n>=15 sayilmali."""
    satirlar = []
    for i in range(15):
        satirlar.append(kayit(i))
        if i % 5 == 0:
            satirlar.append("}} bozuk satir %d" % i)
    defter_yaz(kok, "karisik", satirlar)
    proc = calistir(kok, "karisik")
    metin = dayanikli_olmali(proc, kok, "karisik")
    if metin is None:
        return
    assert not yetersiz_gecer(bolum(metin, 2)), (
        "15 gecerli kayit var ama arac hala 'YETERSIZ VERI' diyor:\n%s"
        % bolum(metin, 2)[:600]
    )


@gerekli
def test_json_satiri_liste_veya_skaler(kok):
    """Gecerli JSON ama nesne olmayan satirlar (liste, sayi, null, string)."""
    satirlar = ["[1, 2, 3]", "42", "null", "\"merhaba\"", "true"]
    satirlar.extend(kayitlar(3))
    defter_yaz(kok, "tuhaf", satirlar)
    proc = calistir(kok, "tuhaf")
    dayanikli_olmali(proc, kok, "tuhaf")


@gerekli
@pytest.mark.parametrize("n", [10, 17])
def test_olcum_alani_eksik(kok, n):
    """
    `olcum` alani hic olmayan kayitlar.
    n=17 kritik: sinirin USTUNDE, yani toplu analiz yolu bu bozuk kayda dokunuyor.
    Ilk kayit da bilerek bozuk (kayitlar[0] varsayimini kiran tuzak).
    """
    satirlar = kayitlar(n)
    satirlar[0] = kayit(0, olcum=_SIL)
    satirlar[3] = kayit(3, olcum=_SIL)
    satirlar[n - 1] = kayit(n - 1, olcum=_SIL)
    defter_yaz(kok, "eksikolcum", satirlar)
    proc = calistir(kok, "eksikolcum")
    dayanikli_olmali(proc, kok, "eksikolcum")


@gerekli
def test_tum_kayitlarda_olcum_eksik(kok):
    """En sert hali: sinirin ustunde kayit var ama hicbirinde olcum yok."""
    satirlar = [kayit(i, olcum=_SIL) for i in range(16)]
    defter_yaz(kok, "hicolcum", satirlar)
    proc = calistir(kok, "hicolcum")
    metin = dayanikli_olmali(proc, kok, "hicolcum")
    if metin is not None:
        bolum3_dolu_kontrol(metin)


@gerekli
def test_olcum_none_ve_bos_sozluk(kok):
    satirlar = kayitlar(16)
    satirlar[2] = kayit(2, olcum=None)
    satirlar[5] = kayit(5, olcum={})
    defter_yaz(kok, "olcumnone", satirlar)
    proc = calistir(kok, "olcumnone")
    dayanikli_olmali(proc, kok, "olcumnone")


@gerekli
def test_lufs_none(kok):
    satirlar = kayitlar(16)
    for i in (0, 4, 9):
        satirlar[i] = kayit(i, olcum={"lufs": None, "true_peak": None, "lra": None})
    defter_yaz(kok, "lufsnone", satirlar)
    proc = calistir(kok, "lufsnone")
    dayanikli_olmali(proc, kok, "lufsnone")


@gerekli
def test_tum_kayitlarda_lufs_none(kok):
    """En sert hali: hicbir kayitta ses olcumu yok."""
    satirlar = [kayit(i, olcum={"lufs": None, "ses_var": False}) for i in range(18)]
    defter_yaz(kok, "sessiz", satirlar)
    proc = calistir(kok, "sessiz")
    metin = dayanikli_olmali(proc, kok, "sessiz")
    if metin is not None:
        bolum3_dolu_kontrol(metin)


@gerekli
def test_izlenme_none(kok):
    satirlar = kayitlar(17)
    for i in (0, 1, 6, 11):
        satirlar[i] = kayit(i, sonuc={"izlenme": None})
    satirlar[15] = kayit(15, sonuc=_SIL)
    defter_yaz(kok, "izlnone", satirlar)
    proc = calistir(kok, "izlnone")
    dayanikli_olmali(proc, kok, "izlnone")


@gerekli
def test_tum_izlenmeler_ayni_sifira_bolme(kok):
    """Varyans sifir: yuzde degisim / normalizasyon hesaplari patlamamali."""
    satirlar = [kayit(i, sonuc={"izlenme": 500, "begeni": 0}) for i in range(20)]
    defter_yaz(kok, "duz", satirlar)
    proc = calistir(kok, "duz")
    metin = dayanikli_olmali(proc, kok, "duz")
    if metin is not None:
        bolum3_dolu_kontrol(metin)


@gerekli
def test_tum_izlenmeler_sifir(kok):
    satirlar = [kayit(i, sonuc={"izlenme": 0, "begeni": 0}) for i in range(16)]
    defter_yaz(kok, "sifir", satirlar)
    proc = calistir(kok, "sifir")
    metin = dayanikli_olmali(proc, kok, "sifir")
    if metin is not None:
        bolum3_dolu_kontrol(metin)


@gerekli
def test_tek_kayit_n1(kok):
    defter_yaz(kok, "tek", [kayit(0)])
    proc = calistir(kok, "tek")
    metin = dayanikli_olmali(proc, kok, "tek")
    if metin is None:
        return
    assert yetersiz_gecer(bolum(metin, 2)), "n=1 iken 2. bolum yetersiz demiyor"
    assert yetersiz_gecer(bolum(metin, 4)), "n=1 iken 4. bolum yetersiz demiyor"
    bolum3_dolu_kontrol(metin)


@gerekli
def test_asiri_buyuk_ve_sifir_degerler(kok):
    """999999999 izlenme, 0.0 sure, 0 kelime, 0 fps: tasma ve sifira bolme tuzagi."""
    satirlar = []
    for i in range(16):
        if i % 2 == 0:
            satirlar.append(
                kayit(
                    i,
                    kelime=0,
                    wpm=0,
                    olcum={
                        "sure": 0.0,
                        "fps": 0.0,
                        "kesme_sayisi": 0,
                        "kesme_per_10sn": 0.0,
                        "en_uzun_plan": 0.0,
                        "ort_plan": 0.0,
                        "cozunurluk": "0x0",
                    },
                    sonuc={"izlenme": 999999999, "begeni": 999999999},
                )
            )
        else:
            satirlar.append(
                kayit(
                    i,
                    kelime=10 ** 9,
                    wpm=10 ** 9,
                    olcum={"sure": 1e9, "lufs": -1e9, "true_peak": 1e9},
                    sonuc={"izlenme": 0, "begeni": 0},
                )
            )
    defter_yaz(kok, "asiri", satirlar)
    proc = calistir(kok, "asiri")
    metin = dayanikli_olmali(proc, kok, "asiri")
    if metin is not None:
        assert re.search(r"\bnan\b", metin, re.IGNORECASE) is None, "Ciktida NaN sizmis"
        assert re.search(r"\binf(inity)?\b", metin, re.IGNORECASE) is None, (
            "Ciktida inf sizmis"
        )
        bolum3_dolu_kontrol(metin)


@gerekli
def test_negatif_ve_yanlis_tipli_degerler(kok):
    """izlenme string, sure negatif, kesme_sayisi string: tip hatasi patlatmamali."""
    satirlar = kayitlar(16)
    satirlar[0] = kayit(0, sonuc={"izlenme": "1155"})
    satirlar[1] = kayit(1, sonuc={"izlenme": -5})
    satirlar[2] = kayit(2, olcum={"sure": -3.0, "kesme_sayisi": "iki"})
    satirlar[3] = kayit(3, olcum={"fps": "30"}, kelime="otuz")
    defter_yaz(kok, "tipler", satirlar)
    proc = calistir(kok, "tipler")
    dayanikli_olmali(proc, kok, "tipler")


# ------------------------------------------------------------------ UNICODE


@gerekli
def test_unicode_baslik_ve_emoji(kok):
    """Turkce karakter + emoji basliklar: dosya utf-8 okunmali, cikti utf-8 olmali."""
    tuhaf_basliklar = [
        "Cigdem'in Sirri \U0001F525",
        "Şu İşe Yarar mı? \U0001F914",
        "Çok özel bir gün \U0001F947",
        "İİİ ııı Ğğ Şş Üü",
        "emoji zinciri \U0001F600\U0001F601\U0001F602\U0001F923",
    ]
    satirlar = []
    for i in range(18):
        satirlar.append(kayit(i, baslik=tuhaf_basliklar[i % len(tuhaf_basliklar)]))
    defter_yaz(kok, "unicode", satirlar)
    proc = calistir(kok, "unicode")
    metin = dayanikli_olmali(proc, kok, "unicode")
    if metin is None:
        return
    # ham baytlar da katı utf-8 olmali (beyin_oku zaten dogruluyor)
    ham = beyin_yolu(kok, "unicode").read_bytes()
    ham.decode("utf-8")
    assert "�" not in metin, "Ciktida bozuk karakter (U+FFFD) var"


@gerekli
def test_unicode_kanal_icinde_baslik_tekrar_etmis(kok):
    """Ayni unicode baslik cok kez gecince gruplama/sayma patlamamali."""
    satirlar = [
        kayit(i, baslik="Aynı başlık \U0001F525") for i in range(15)
    ]
    defter_yaz(kok, "tekrar", satirlar)
    proc = calistir(kok, "tekrar")
    dayanikli_olmali(proc, kok, "tekrar")


@gerekli
def test_utf8_bom_ile_baslayan_defter(kok):
    """BOM'lu dosya: ilk satir bozuk JSON gibi gorunur, arac cokmemeli."""
    hedef = kok / "kanallar" / "bom" / "defter.jsonl"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    govde = "\n".join(json.dumps(k, ensure_ascii=False) for k in kayitlar(16)) + "\n"
    hedef.write_bytes(b"\xef\xbb\xbf" + govde.encode("utf-8"))
    proc = calistir(kok, "bom")
    dayanikli_olmali(proc, kok, "bom")


@gerekli
def test_crlf_satir_sonlari(kok):
    hedef = kok / "kanallar" / "crlf" / "defter.jsonl"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    govde = "\r\n".join(json.dumps(k, ensure_ascii=False) for k in kayitlar(15))
    hedef.write_bytes((govde + "\r\n").encode("utf-8"))
    proc = calistir(kok, "crlf")
    metin = dayanikli_olmali(proc, kok, "crlf")
    if metin is not None:
        assert not yetersiz_gecer(bolum(metin, 2)), (
            "CRLF dosyada 15 kayit var ama yetersiz veri deniyor"
        )


@gerekli
def test_son_satirda_satir_sonu_yok(kok):
    defter_yaz(kok, "sonsatir", kayitlar(15), son_satir_sonu=False)
    proc = calistir(kok, "sonsatir")
    metin = dayanikli_olmali(proc, kok, "sonsatir")
    if metin is not None:
        assert not yetersiz_gecer(bolum(metin, 2)), (
            "Son satirda \\n yok diye 15. kayit yutulmus (n=14 sanilmis)"
        )


# --------------------------------------------------------------- DAVRANIS


@gerekli
def test_iki_kez_calistirinca_uzerine_yazar(kok):
    defter_yaz(kok, "tekrarli", kayitlar(16))
    proc1 = calistir(kok, "tekrarli")
    metin1 = basarili_olmali(proc1, kok, "tekrarli")
    proc2 = calistir(kok, "tekrarli")
    metin2 = basarili_olmali(proc2, kok, "tekrarli")
    for baslik in BASLIKLAR:
        assert metin2.count(baslik) == 1, (
            "Ikinci calistirmada dosyaya eklenmis (append), uzerine yazilmamis: %r"
            % baslik
        )
    assert len(metin2) < len(metin1) * 3, "Cikti ikinci kosuda sismis"


@gerekli
def test_yeterliden_yetersize_gecis_temiz(kok):
    """Once 20 kayit, sonra 14 kayit: eski iddialar dosyada kalmamali."""
    defter_yaz(kok, "gecis", kayitlar(20))
    basarili_olmali(calistir(kok, "gecis"), kok, "gecis")
    defter_yaz(kok, "gecis", kayitlar(14))
    metin = basarili_olmali(calistir(kok, "gecis"), kok, "gecis")
    assert YETERSIZ in bolum(metin, 2), (
        "n 20'den 14'e dusunce 2. bolum hala yetersiz demiyor (bayat cikti?)"
    )
    for kalip in KARSILASTIRMA_KALIPLARI:
        assert re.search(kalip, bolum(metin, 2), re.IGNORECASE) is None, (
            "n=14'e dusunce eski sayisal iddia hala duruyor (kalip=%r)" % kalip
        )


@gerekli
def test_baska_kanali_kirletmez(kok):
    defter_yaz(kok, "a", kayitlar(16))
    defter_yaz(kok, "b", kayitlar(3))
    basarili_olmali(calistir(kok, "a"), kok, "a")
    assert not beyin_yolu(kok, "b").exists(), (
        "a kanali islenirken b kanalina da yazilmis"
    )


@gerekli
def test_defter_dosyasi_degistirilmez(kok):
    hedef = defter_yaz(kok, "korunan", kayitlar(16))
    once = hedef.read_bytes()
    basarili_olmali(calistir(kok, "korunan"), kok, "korunan")
    assert hedef.read_bytes() == once, "Arac defter.jsonl dosyasini degistirmis"


@gerekli
def test_ag_cagrisi_yapilmadan_biter(kok):
    """
    Proxy'ler olu porta bakiyor. `beyin` komutu sadece dosya okuyup yazmali,
    bu yuzden zaman asimina ugramadan ve ag hatasi vermeden bitmeli.
    """
    defter_yaz(kok, "agsiz", kayitlar(16))
    proc = calistir(kok, "agsiz")
    metin = basarili_olmali(proc, kok, "agsiz")
    tumu = _normalize((proc.stdout or "") + (proc.stderr or ""))
    for iz in ("CONNECTIONERROR", "MAX RETRIES", "URLLIB", "HTTPSCONNECTIONPOOL"):
        assert iz not in tumu, "beyin komutu ag cagrisi denemis: %s" % iz
    assert metin


@gerekli
def test_bilinmeyen_komut_traceback_dokmez(kok):
    defter_yaz(kok, "ornek", kayitlar(16))
    proc = calistir(kok, "ornek", komut="boyle-bir-komut-yok")
    traceback_yok(proc)
    assert proc.returncode != 0, "Bilinmeyen komut 0 ile cikmamali"
