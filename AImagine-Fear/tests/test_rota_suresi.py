"""Rock 2: rota suresi rotadan okunur ve yetenek matrisiyle dogrulanir.

Bu testlerin ortak amaci tek bir sey: DOGRULANMAMIS bir sure hicbir kosulda
kredi harcayan cagriya ulasmasin.
"""
from __future__ import annotations

import shutil
import sys
import uuid
from pathlib import Path

import pytest

PROJE_KOKU = Path(__file__).resolve().parent.parent
if str(PROJE_KOKU) not in sys.path:
    sys.path.insert(0, str(PROJE_KOKU))

from profil import YETENEK_MATRISI, matris_anahtari  # noqa: E402
from tools import gunluk  # noqa: E402


def _gecici_proje(duration_satiri: str | None) -> Path:
    """Gercek bir rotayi kopyalayip DURATION satirini degistir.

    Gercek rota dosyalarina ASLA dokunmuyoruz.
    """
    kok = PROJE_KOKU / "tests" / ".rota-tmp" / uuid.uuid4().hex[:8]
    (kok / "routes").mkdir(parents=True)
    kaynak = (PROJE_KOKU / "routes" / "dubai-burj-altin.md").read_text(encoding="utf-8")
    satirlar = []
    for satir in kaynak.splitlines():
        if satir.startswith("DURATION:"):
            if duration_satiri is None:
                continue  # alani tamamen sil
            satirlar.append(duration_satiri)
        else:
            satirlar.append(satir)
    (kok / "routes" / "dubai-burj-altin.md").write_text(
        "\n".join(satirlar) + "\n", encoding="utf-8", newline="\n"
    )
    return kok


# ----------------------------------------------------------------------
# Gercek rotalardan dogru okuma
# ----------------------------------------------------------------------
def test_dubai_15_okunur() -> None:
    assert gunluk.rota_suresi("dubai-burj-altin") == 15


def test_toronto_20_okunur_ama_siradan_cikarilmis() -> None:
    assert gunluk.rota_suresi("toronto-cn-red-dusk") == 20
    assert "toronto-cn-red-dusk" not in gunluk.SIRA, (
        "20 saniyelik rota donusum havuzunda; matriste karsiligi yok"
    )


def test_25_saniyelik_rota_da_siradan_cikarilmis() -> None:
    assert gunluk.rota_suresi("vegas-strat-blue-rain-25") == 25
    assert "vegas-strat-blue-rain-25" not in gunluk.SIRA


# ----------------------------------------------------------------------
# SIRA butunlugu. "Bos gecen test kanit degildir": once bos olmadigini kanitla.
# ----------------------------------------------------------------------
def test_sira_bos_degil_tekrarsiz_ve_tamami_matriste() -> None:
    assert gunluk.SIRA, "SIRA bos"
    assert len(gunluk.SIRA) == len(set(gunluk.SIRA)), "SIRA'da tekrar var"
    profil = gunluk.PROFILLER["720p"]  # dogrulanmis profil
    for slug in gunluk.SIRA:
        sure = gunluk.rota_suresi(slug)
        anahtar = matris_anahtari(
            gunluk.MODEL, sure, profil["cozunurluk"], profil["beklenen_fps"]
        )
        assert anahtar in YETENEK_MATRISI, (
            "%s (%s sn) SIRA'da ama matriste karsiligi yok" % (slug, sure)
        )


def test_sira_rota_dosyalarini_silmedi() -> None:
    """Havuzdan cikarmak dosyayi silmek DEGIL."""
    for slug in ("toronto-cn-red-dusk", "vegas-strat-blue-rain", "vegas-strat-blue-rain-25"):
        assert (PROJE_KOKU / "routes" / (slug + ".md")).exists(), (
            "%s rota dosyasi silinmis" % slug
        )


# ----------------------------------------------------------------------
# Bozuk DURATION vakalari. Her birinde SIFIR uretim cagrisi.
# ----------------------------------------------------------------------
@pytest.mark.parametrize("duration_satiri", [
    None,                    # alan hic yok
    "DURATION: ",            # bos
    "DURATION: abc",         # sayi degil
    "DURATION: 0",           # sifir
    "DURATION: -5",          # negatif
    "DURATION: 12.5",        # kesirli , kie_uret int() ile kirpar
    "DURATION: nan",         # sonlu degil
])
def test_bozuk_duration_reddedilir(duration_satiri: str | None) -> None:
    kok = _gecici_proje(duration_satiri)
    try:
        with pytest.raises(gunluk.SureHatasi):
            gunluk.rota_suresi("dubai-burj-altin", kok=kok)
    finally:
        shutil.rmtree(kok, ignore_errors=True)


def test_olmayan_rota_reddedilir() -> None:
    with pytest.raises(gunluk.SureHatasi):
        gunluk.rota_suresi("boyle-bir-rota-yok")


# ----------------------------------------------------------------------
# En onemli test: matriste olmayan sure URETIME ULASAMAZ.
# ----------------------------------------------------------------------
def test_matriste_olmayan_sure_uretim_cagrisi_yapmaz(monkeypatch, capsys) -> None:
    cagrilar: list[list[str]] = []

    def _tuzak(cmd, cwd):  # pragma: no cover , cagrilirsa test zaten duser
        cagrilar.append(cmd)
        raise AssertionError("URETIM CAGRISI YAPILDI: %s" % cmd)

    monkeypatch.setattr(gunluk, "kosa", _tuzak)
    monkeypatch.setattr(gunluk, "kredi", lambda: pytest.fail("KREDI OKUNDU"))
    monkeypatch.setattr(gunluk, "rota_suresi", lambda slug, kok=None: 20)

    kod = gunluk.main(["--sehir", "toronto-cn-red-dusk", "--profil", "720p"])
    assert kod == 1
    assert cagrilar == [], "matriste olmayan sure icin uretim cagrisi yapildi"
    assert "matrisinde YOK" in capsys.readouterr().out


def test_okunamayan_sure_uretim_cagrisi_yapmaz(monkeypatch) -> None:
    def _tuzak(cmd, cwd):  # pragma: no cover
        raise AssertionError("URETIM CAGRISI YAPILDI: %s" % cmd)

    monkeypatch.setattr(gunluk, "kosa", _tuzak)
    monkeypatch.setattr(gunluk, "kredi", lambda: pytest.fail("KREDI OKUNDU"))

    def _patla(slug, kok=None):
        raise gunluk.SureHatasi("test")

    monkeypatch.setattr(gunluk, "rota_suresi", _patla)
    assert gunluk.main(["--sehir", "dubai-burj-altin", "--profil", "720p"]) == 1


# ----------------------------------------------------------------------
# Sure gercekten uctan uca akiyor mu: argv, kapi ve matris ayni sayiyi gormeli.
# ----------------------------------------------------------------------
def test_sure_argv_ve_kapiya_ayni_gider() -> None:
    profil = gunluk.PROFILLER["720p"]
    argv = gunluk.uretim_komutu("dubai-burj-altin", 15, profil)
    assert "--n-frames" in argv
    assert argv[argv.index("--n-frames") + 1] == "15"

    probe = {
        "streams": [
            {"codec_type": "video", "width": 720, "height": 1280, "r_frame_rate": "24/1"},
            {"codec_type": "audio", "r_frame_rate": "0/0"},
        ],
        "format": {"duration": "15.0"},
    }
    assert gunluk.denetle_akislar(probe, 5_000_000, 15, profil) == []
    # 20 saniyelik beklenti ayni videoyu DUSURMELI
    sorunlar = gunluk.denetle_akislar(probe, 5_000_000, 20, profil)
    assert any("sure" in s for s in sorunlar), (
        "15 sn'lik video 20 sn beklentisiyle gecti , kapi kendi sabitine bakiyor"
    )


def test_yayin_izni_sureye_duyarli() -> None:
    """Ayni profil, farkli sure: 15 dogrulanmis, 20 matriste yok."""
    izinli15, _ = gunluk.yayin_izni("720p", 15)
    assert izinli15 is True
    izinli20, durum20 = gunluk.yayin_izni("720p", 20)
    assert izinli20 is False
    assert durum20 == "matriste yok"
