"""Rock 5 uctan uca: baslik secimi ve etiketlerin gercekten gitmesi.

Bu dosya baslik.py'nin saf mantigini DEGIL, uretim hattina baglanmasini test eder.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJE_KOKU = Path(__file__).resolve().parent.parent
if str(PROJE_KOKU) not in sys.path:
    sys.path.insert(0, str(PROJE_KOKU))

from tools import gunluk  # noqa: E402


# ----------------------------------------------------------------------
# Etiket turetimi: kanon tek kaynak
# ----------------------------------------------------------------------
def test_etiketler_captiondan_turetiliyor() -> None:
    caption = (
        "You're falling past the Burj Khalifa above Dubai.\n\n"
        "#MegaSlideFear #DubaiBurjKhalifa #WaterSlide #POVReels "
        "#CGIAdventure #ViralReels"
    )
    assert gunluk.etiketler(caption) == (
        "MegaSlideFear,DubaiBurjKhalifa,WaterSlide,POVReels,CGIAdventure,ViralReels"
    )


def test_etiketlerde_tekrar_yok_ve_sira_korunuyor() -> None:
    assert gunluk.etiketler("#A #B #a #C #b") == "A,B,C"


def test_etiketsiz_caption_bos_dizge() -> None:
    assert gunluk.etiketler("hic etiket yok") == ""


def test_gercek_rotanin_etiketleri_uretiliyor() -> None:
    # Kaynak rota dosyasi, out/ DEGIL: out/ .gitignore'da ve build.py
    # calismadan bos olur.
    import build

    rota = build.load_route(
        PROJE_KOKU / "routes" / "dubai-burj-altin.md", PROJE_KOKU
    )
    tags = gunluk.etiketler(rota.sections["CAPTION"])
    assert tags.startswith("MegaSlideFear,")
    assert "ViralReels" in tags
    # YouTube'un otomatik copu ARTIK gitmiyor
    assert "camera" not in tags.lower() and "sharing" not in tags.lower()


# ----------------------------------------------------------------------
# Baslik secimi defterden besleniyor
# ----------------------------------------------------------------------
def test_bos_defterde_ilk_varyant(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    cikti = tmp_path / "out" / "s"
    cikti.mkdir(parents=True)
    (cikti / "TITLE.txt").write_text("A drop #shorts\nB drop #shorts", encoding="utf-8")
    secilen, hata = gunluk.baslik_sec("s", [])
    assert (secilen, hata) == ("A drop #shorts", "")


def test_kullanilmis_varyant_atlanir(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    cikti = tmp_path / "out" / "s"
    cikti.mkdir(parents=True)
    (cikti / "TITLE.txt").write_text("A drop #shorts\nB drop #shorts", encoding="utf-8")
    gecmis = [{"title": "A drop #shorts", "kullanildi": True}]
    secilen, _ = gunluk.baslik_sec("s", gecmis)
    assert secilen == "B drop #shorts"


def test_noktalamasi_farkli_kullanim_da_sayilir(monkeypatch, tmp_path: Path) -> None:
    """Yukleyici noktalamayi atiyor; "A drop!" ile "A drop" AYNI baslik."""
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    cikti = tmp_path / "out" / "s"
    cikti.mkdir(parents=True)
    (cikti / "TITLE.txt").write_text("A drop! #shorts\nB drop #shorts", encoding="utf-8")
    gecmis = [{"title": "a drop #shorts", "kullanildi": True}]
    secilen, _ = gunluk.baslik_sec("s", gecmis)
    assert secilen == "B drop #shorts", "normalize esit baslik kullanilmis sayilmadi"


def test_basarisiz_yayinin_basligi_kullanilmis_sayilmaz(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    cikti = tmp_path / "out" / "s"
    cikti.mkdir(parents=True)
    (cikti / "TITLE.txt").write_text("A drop #shorts\nB drop #shorts", encoding="utf-8")
    gecmis = [{"title": "A drop #shorts", "kullanildi": False}]
    secilen, _ = gunluk.baslik_sec("s", gecmis)
    assert secilen == "A drop #shorts", "basarisiz yayin basligi yakildi"


def test_havuz_tukenince_dur(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    cikti = tmp_path / "out" / "s"
    cikti.mkdir(parents=True)
    (cikti / "TITLE.txt").write_text("A drop #shorts\nB drop #shorts", encoding="utf-8")
    gecmis = [
        {"title": "A drop #shorts", "kullanildi": True},
        {"title": "B drop #shorts", "kullanildi": True},
    ]
    secilen, hata = gunluk.baslik_sec("s", gecmis)
    assert secilen is None
    assert "yeni varyant yaz" in hata


# ----------------------------------------------------------------------
# EN KRITIK: havuz tukendiginde kredi harcanmadan durulmali
# ----------------------------------------------------------------------
def test_havuz_tukenince_uretim_ve_kredi_HIC_calismaz(monkeypatch, tmp_path: Path) -> None:
    slug = "vegas-strat-blue-rain-15"
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    monkeypatch.setattr(gunluk, "DEFTER", tmp_path / "yayin.jsonl")
    cikti = tmp_path / "out" / slug
    cikti.mkdir(parents=True)
    (cikti / "CAPTION.txt").write_text("caption #Tag", encoding="utf-8")
    (cikti / "TITLE.txt").write_text("A drop #shorts\nB drop #shorts", encoding="utf-8")

    monkeypatch.setattr(gunluk, "rota_suresi", lambda s, kok=None: 15)
    monkeypatch.setattr(gunluk, "rota_paleti", lambda s, kok=None: "neon")
    monkeypatch.setattr(gunluk, "defter", lambda: [
        {"title": "A drop #shorts", "kullanildi": True},
        {"title": "B drop #shorts", "kullanildi": True},
    ])
    monkeypatch.setattr(gunluk, "kredi", lambda: pytest.fail("KREDI OKUNDU"))

    def _tuzak(cmd, cwd):
        if any("kie_uret" in str(p) for p in cmd):
            pytest.fail("URETIM CAGRISI YAPILDI")
        return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(gunluk, "kosa", _tuzak)
    kod = gunluk.main(["--sehir", slug, "--profil", "720p"])
    assert kod == 1


# ----------------------------------------------------------------------
# Etiketler ve baslik gercekten yayinla.py argv'sine giriyor mu
# ----------------------------------------------------------------------
def test_yayin_argvsinde_baslik_ve_tags_var(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    cikti = tmp_path / "out" / "s"
    cikti.mkdir(parents=True)
    (cikti / "CAPTION.txt").write_text("x #MegaSlideFear #CNTower", encoding="utf-8")
    komut = gunluk._yayin_komutu(
        tmp_path / "m.mp4", "s", False, "CN Tower drop #shorts", "MegaSlideFear,CNTower"
    )
    assert komut is not None
    assert komut[komut.index("--title") + 1] == "CN Tower drop #shorts"
    assert komut[komut.index("--tags") + 1] == "MegaSlideFear,CNTower"


def test_yayinla_tags_argumanini_yayinlaya_gecirir(monkeypatch, tmp_path: Path) -> None:
    """gunluk.yayinla -> yayinla.py argv'si: tags kayboluyor mu?"""
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    cikti = tmp_path / "out" / "s"
    cikti.mkdir(parents=True)
    (cikti / "CAPTION.txt").write_text("x #Tag", encoding="utf-8")
    yakalanan = {}

    def _kosa(cmd, cwd):
        yakalanan["cmd"] = cmd
        return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(gunluk, "kosa", _kosa)
    gunluk.yayinla(tmp_path / "m.mp4", "s", False, {"palet": "neon"},
                   "S drop #shorts", "Tag")
    cmd = yakalanan["cmd"]
    assert cmd[cmd.index("--tags") + 1] == "Tag"
    assert cmd[cmd.index("--title") + 1] == "S drop #shorts"
    ek = json.loads(cmd[cmd.index("--ek-alanlar") + 1])
    assert ek["palet"] == "neon"


# ----------------------------------------------------------------------
# Kanal geneli: iki rota ayni basligi tasimamali
# ----------------------------------------------------------------------
def test_hicbir_iki_rota_ayni_basligi_tasimiyor() -> None:
    """core/uploader.py mukerrer basligi gorunce YouTube'u ATLIYOR.

    Kaynak ROTA DOSYALARI, out/ DEGIL: out/ .gitignore'da ve build.py
    calismadan bos olur. out/'a bakan bir surum, testin build'den sonra
    kosmasina bagli kalirdi ve taze bir checkout'ta yanlis sebeple duserdi.
    """
    import baslik
    import build

    gorulen: dict[str, str] = {}
    rotalar = [
        yol for yol in sorted((PROJE_KOKU / "routes").glob("*.md"))
        if not yol.name.startswith("_")
    ]
    assert rotalar, "hic rota bulunamadi"
    for yol in rotalar:
        rota = build.load_route(yol, PROJE_KOKU)
        for satir in rota.sections["TITLE"].splitlines():
            if not satir.strip():
                continue
            norm = baslik.normalize(satir)
            assert norm not in gorulen, (
                "%s ile %s ayni basligi tasiyor: %r"
                % (gorulen.get(norm), rota.slug, satir)
            )
            gorulen[norm] = rota.slug
    assert len(gorulen) >= 2 * len(rotalar), (
        "her rotada en az 2 varyant olmali, toplam %d baslik / %d rota"
        % (len(gorulen), len(rotalar))
    )
