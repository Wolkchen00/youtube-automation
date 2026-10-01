"""KAPI konsepti: ilk kareden baslayan, bulut kapisindan felakete giren 15 sn video.

2026-10-01 Ihsan karari: mevsim kapisi A/B'sinde 15 sn'lik A kazandi, otomasyon
bu konseptten devam eder (farkli felaketler, farkli hava). Iki ders koda gecti:
metinden video bacaklari bozdu, ILK KARE kilidi duzeltti; ve rider konusmaz.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

PROJE_KOKU = Path(__file__).resolve().parent.parent
if str(PROJE_KOKU) not in sys.path:
    sys.path.insert(0, str(PROJE_KOKU))

import build  # noqa: E402
from tools import gunluk, ilk_kare  # noqa: E402

ORNEK = "giza-piramit-kum-firtinasi"


def _proje(tmp_path: Path, rota_metni: str | None = None) -> Path:
    shutil.copytree(PROJE_KOKU / "canon", tmp_path / "canon")
    (tmp_path / "routes").mkdir()
    metin = rota_metni or (PROJE_KOKU / "routes" / (ORNEK + ".md")).read_text(encoding="utf-8")
    (tmp_path / "routes" / (ORNEK + ".md")).write_text(metin, encoding="utf-8")
    return tmp_path


def _bozuk(degistir) -> str:
    return degistir((PROJE_KOKU / "routes" / (ORNEK + ".md")).read_text(encoding="utf-8"))


# ----------------------------------------------------------------------
# build.py
# ----------------------------------------------------------------------
def test_kapi_rotasi_kendi_kanonuyla_kurulur(tmp_path: Path) -> None:
    kok = _proje(tmp_path)
    rotalar = build.build_project(kok, check=True)
    assert [r.konsept for r in rotalar] == ["kapi"]
    cikti = kok / "out" / ORNEK
    prompt = (cikti / "PROMPT.txt").read_text(encoding="utf-8")
    assert "THE CLOUD GATE RULE" in prompt
    assert "a towering haboob sandstorm" in prompt  # <<FELAKET>> cozuldu
    assert "THE RIDER NEVER SPEAKS" in prompt
    assert "landing pool" in prompt.split("NEGATIVE\n", 1)[1]  # havuz yasak
    assert "<<" not in prompt
    ilk = (cikti / "ILK_KARE.txt").read_text(encoding="utf-8")
    assert "Pyramids of Giza at sunrise" in ilk
    assert "electric cyan" in ilk and "<<" not in ilk


def test_havuz_rotalari_degismedi(tmp_path: Path) -> None:
    shutil.copytree(PROJE_KOKU / "canon", tmp_path / "canon")
    (tmp_path / "routes").mkdir()
    shutil.copy(PROJE_KOKU / "routes" / "dubai-burj-altin.md", tmp_path / "routes")
    rota = build.build_project(tmp_path, check=True)[0]
    assert rota.konsept == "havuz"
    assert not (tmp_path / "out" / "dubai-burj-altin" / "ILK_KARE.txt").exists()
    prompt = (tmp_path / "out" / "dubai-burj-altin" / "PROMPT.txt").read_text(encoding="utf-8")
    assert "CLOUD GATE RULE" not in prompt


@pytest.mark.parametrize("bozucu", [
    lambda m: "\n".join(s for s in m.splitlines() if not s.startswith("FELAKET:")),
    lambda m: m.replace("## ILK KARE", "## BASKA BOLUM"),
    lambda m: m.replace("KONSEPT: kapi", "KONSEPT: kapı"),
    lambda m: m.replace("A sharp gasp, then a held breath.", '"Oh my god."'),
])
def test_bozuk_kapi_rotasi_kapida_kalir(tmp_path: Path, bozucu) -> None:
    kok = _proje(tmp_path, _bozuk(bozucu))
    with pytest.raises(build.BuildError):
        build.build_project(kok, check=True)


# ----------------------------------------------------------------------
# gunluk.py
# ----------------------------------------------------------------------
def test_uretim_komutu_ilk_kareyi_gecirir() -> None:
    profil = gunluk.PROFILLER["720p"]
    assert "--first-frame-url" not in gunluk.uretim_komutu("s", 15, profil)
    komut = gunluk.uretim_komutu("s", 15, profil, "https://x/y.jpg")
    assert komut[komut.index("--first-frame-url") + 1] == "https://x/y.jpg"


def test_gercek_ornek_rota_kapi_konseptinde() -> None:
    assert gunluk.rota_konsepti(ORNEK) == "kapi"
    assert gunluk.rota_konsepti("dubai-burj-altin") == "havuz"


def _kapi_sahnesi(tmp_path: Path, monkeypatch, cagrilar: list):
    slug = "test-kapi"
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    monkeypatch.setattr(gunluk, "DEFTER", tmp_path / "yayin.jsonl")
    cikti = tmp_path / "out" / slug
    cikti.mkdir(parents=True)
    (cikti / "CAPTION.txt").write_text("caption #Tag", encoding="utf-8")
    (cikti / "TITLE.txt").write_text(
        "Test Tower glass drop #shorts\nI slid off the Test Tower #shorts", encoding="utf-8")
    monkeypatch.setattr(gunluk, "defter", lambda: [])
    monkeypatch.setattr(gunluk, "kredi", lambda: 10000)
    monkeypatch.setattr(gunluk, "rota_suresi", lambda s, kok=None: 15)
    monkeypatch.setattr(gunluk, "rota_paleti", lambda s, kok=None: "neon")
    monkeypatch.setattr(gunluk, "rota_konsepti", lambda s, kok=None: "kapi")

    def _kosa(cmd, cwd):
        cagrilar.append([str(c) for c in cmd])
        if "kie_uret.py" in " ".join(cagrilar[-1]):
            return gunluk.subprocess.CompletedProcess(cmd, 1, "", "durdur")
        return gunluk.subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(gunluk, "kosa", _kosa)
    return slug


def test_kapi_rotasi_videoyu_ilk_kareden_baslatir(tmp_path, monkeypatch) -> None:
    cagrilar: list = []
    slug = _kapi_sahnesi(tmp_path, monkeypatch, cagrilar)
    monkeypatch.setattr(ilk_kare, "hazirla", lambda s, kok=None: ("https://kare/1.jpg", "onayli"))
    # Uretim komutu kasitli olarak basarisiz donuyor; bakilan sey argv.
    assert gunluk.main(["--sehir", slug]) == 1
    uretim = [c for c in cagrilar if "kie_uret.py" in " ".join(c)]
    assert uretim, "uretim komutu hic calismadi"
    assert uretim[0][uretim[0].index("--first-frame-url") + 1] == "https://kare/1.jpg"


def test_ilk_kare_hazirlanamazsa_seedance_cagrilmaz(tmp_path, monkeypatch) -> None:
    cagrilar: list = []
    slug = _kapi_sahnesi(tmp_path, monkeypatch, cagrilar)

    def _patla(s, kok=None):
        raise ilk_kare.IlkKareHatasi("gorsel yok")

    monkeypatch.setattr(ilk_kare, "hazirla", _patla)
    assert gunluk.main(["--sehir", slug]) == 1
    assert not [c for c in cagrilar if "kie_uret.py" in " ".join(c)], "kredi yanardi"


def test_kapi_kredi_on_kontrolu_gorsel_payini_sayar(tmp_path, monkeypatch) -> None:
    cagrilar: list = []
    slug = _kapi_sahnesi(tmp_path, monkeypatch, cagrilar)
    # Videoya yeter, gorsel payina yetmez: kredi harcamadan durmali.
    monkeypatch.setattr(gunluk, "kredi", lambda: gunluk.gerekli_kredi("720p", 15) + 1)
    monkeypatch.setattr(ilk_kare, "hazirla", lambda *a, **k: pytest.fail("gorsel uretildi"))
    assert gunluk.main(["--sehir", slug]) == 1


# ----------------------------------------------------------------------
# tools/ilk_kare.py
# ----------------------------------------------------------------------
def test_onayli_gorsel_varsa_uretilmez(tmp_path, monkeypatch) -> None:
    (tmp_path / "ilk_kare").mkdir()
    (tmp_path / "ilk_kare" / "r.jpg").write_bytes(b"jpg")
    monkeypatch.setattr(ilk_kare, "yukle", lambda yol: "https://yuklendi/" + yol.name)
    monkeypatch.setattr(ilk_kare, "uret", lambda *a: pytest.fail("onayli varken uretildi"))
    url, kaynak = ilk_kare.hazirla("r", tmp_path)
    assert url == "https://yuklendi/r.jpg" and kaynak.startswith("onayli")


def test_onayli_yoksa_ilk_kare_promptundan_uretir(tmp_path, monkeypatch) -> None:
    (tmp_path / "out" / "r").mkdir(parents=True)
    (tmp_path / "out" / "r" / "ILK_KARE.txt").write_text("sahne", encoding="utf-8")
    monkeypatch.setattr(ilk_kare, "uret", lambda prompt, hedef: "https://uretildi/" + prompt)
    assert ilk_kare.hazirla("r", tmp_path) == ("https://uretildi/sahne", "uretildi")


def test_ilk_kare_promptu_da_yoksa_hata(tmp_path) -> None:
    with pytest.raises(ilk_kare.IlkKareHatasi):
        ilk_kare.hazirla("yok", tmp_path)


def test_kamera_silme_her_uretimde_kosar(tmp_path, monkeypatch) -> None:
    gorseller = []

    def _gorsel(prompt, referans=None):
        gorseller.append(referans)
        return "https://g/%d.png" % len(gorseller)

    monkeypatch.setattr(ilk_kare, "_gorsel", _gorsel)
    monkeypatch.setattr(ilk_kare.requests, "get",
                        lambda url, timeout: type("Y", (), {"content": b"png"})())
    assert ilk_kare.uret("sahne", tmp_path / "k.png") == "https://g/2.png"
    assert gorseller == [None, "https://g/1.png"], "duzenleme ham gorsel uzerinde kosmali"


def test_kamera_silme_basarisizsa_ham_gorselle_devam(tmp_path, monkeypatch) -> None:
    def _gorsel(prompt, referans=None):
        if referans:
            raise ilk_kare.IlkKareHatasi("duzenleme bos")
        return "https://g/ham.png"

    monkeypatch.setattr(ilk_kare, "_gorsel", _gorsel)
    monkeypatch.setattr(ilk_kare.requests, "get",
                        lambda url, timeout: type("Y", (), {"content": b"png"})())
    assert ilk_kare.uret("sahne", tmp_path / "k.png") == "https://g/ham.png"
