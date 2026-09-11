"""Kredi yetersizligi: kredi harcamadan dur, damga birak, ayni gun telafi et.

2026-09-11 vakasi: bakiye 1523, 1080p is 1500'den pahali, Kie createTask'i
402 ile reddetti. Otomatik yukleme 1500'un ALTINDA tetiklendigi icin o da
gelmedi ve kanal o gun videosuz kaldi. 700'luk taban bunu goremiyordu.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

PROJE_KOKU = Path(__file__).resolve().parent.parent
if str(PROJE_KOKU) not in sys.path:
    sys.path.insert(0, str(PROJE_KOKU))

from tools import gunluk  # noqa: E402


# Kosu 34625373310'un stderr'i, birebir.
GERCEK_402 = (
    'createTask reddetti: {"code":402,"msg":"Credits insufficient : Your current '
    "balance isn’t enough to run this request. Please top up to continue.\","
    '"data":null}'
)


def _bugun() -> str:
    return datetime.now(gunluk.LA).strftime("%Y-%m-%d")


# ----------------------------------------------------------------------
# 402 tanima: yalniz OLUSMAMIS gorev sayilir
# ----------------------------------------------------------------------
def test_gercek_402_mesaji_taniniyor() -> None:
    assert gunluk.kredi_reddi_mi(GERCEK_402) is True


def test_http_402_taniniyor() -> None:
    assert gunluk.kredi_reddi_mi("createTask HTTP 402\n{}") is True


@pytest.mark.parametrize("metin", [
    "",
    'createTask reddetti: {"code":422,"msg":"prompt too long"}',
    'Uretim basarisiz: {"code":402,"state":"fail"}',  # gorev OLUSMUSTU
    "Zaman asimi: 1800s icinde bitmedi. taskId=abc",
    "createTask HTTP 4020",
])
def test_baska_hatalar_kredi_reddi_sayilmaz(metin: str) -> None:
    assert gunluk.kredi_reddi_mi(metin) is False


def test_gerekli_kredi_olculmemis_cozunurlukte_tabana_duser(monkeypatch) -> None:
    monkeypatch.setattr(gunluk, "KREDI_15SN", {"720p": 615})
    assert gunluk.gerekli_kredi("720p", 15) == 700  # taban olculenden buyuk
    assert gunluk.gerekli_kredi("480p", 15) == gunluk.MIN_KREDI
    monkeypatch.setattr(gunluk, "KREDI_15SN", {"1080p": 1600})
    assert gunluk.gerekli_kredi("1080p", 15) == 1600


# ----------------------------------------------------------------------
# main(): kredi durusu damga birakir, baska durus birakmaz
# ----------------------------------------------------------------------
def _sahne(tmp_path: Path, monkeypatch, bakiye: float, uretim_stderr: str | None):
    """main()'i uretim adimina kadar gotur. uretim_stderr None ise uretim
    komutu calisirsa test DUSER."""
    slug = "test-slug"
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    monkeypatch.setattr(gunluk, "DEFTER", tmp_path / "yayin.jsonl")
    cikti = tmp_path / "out" / slug
    cikti.mkdir(parents=True)
    (cikti / "CAPTION.txt").write_text("caption #Tag", encoding="utf-8")
    (cikti / "TITLE.txt").write_text(
        "Test Tower glass drop #shorts\nI slid off the Test Tower #shorts",
        encoding="utf-8",
    )
    monkeypatch.setattr(gunluk, "defter", lambda: [])
    monkeypatch.setattr(gunluk, "kredi", lambda: bakiye)
    monkeypatch.setattr(gunluk, "rota_suresi", lambda s, kok=None: 15)
    monkeypatch.setattr(gunluk, "rota_paleti", lambda s, kok=None: "neon")
    monkeypatch.setattr(gunluk, "KREDI_15SN", {"1080p": 1600})

    def _kosa(cmd, cwd):
        if any("kie_uret" in str(p) for p in cmd):
            if uretim_stderr is None:
                pytest.fail("KREDI YETERSIZKEN URETIM CALISTI: %s" % cmd)
            return type("R", (), {"returncode": 1, "stdout": "kredi once : %s\n" % bakiye,
                                  "stderr": uretim_stderr})()
        return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(gunluk, "kosa", _kosa)
    return slug


def test_varsayilan_profil_otomatik_yukleme_olu_bolgesine_dusmez() -> None:
    """Kie otomatik yuklemesi bakiye 1500'un ALTINA dusunce tetikleniyor. Is
    bundan ucuzsa bakiye hicbir zaman 'yukleme yok ama is de sigmiyor'
    araliginda kalamaz. 1080p (1530) bu araliga dusuyordu, 720p (615) dusmez."""
    gerekli = gunluk.gerekli_kredi(gunluk.PROFILLER[gunluk.VARSAYILAN_PROFIL]["cozunurluk"], 15)
    assert gerekli < 1500


def test_on_kontrol_kie_ye_gitmeden_durur_ve_damgalar(tmp_path: Path, monkeypatch) -> None:
    slug = _sahne(tmp_path, monkeypatch, bakiye=1523.0, uretim_stderr=None)
    assert gunluk.main(["--sehir", slug, "--profil", "1080p"]) == 1
    damga = json.loads(gunluk.KREDI_BEKLIYOR.read_text(encoding="utf-8"))
    assert damga["tarih"] == _bugun()
    assert damga["sebep"] == "on kontrol"
    assert damga["bakiye"] == 1523.0 and damga["gerekli"] == 1600


def test_kie_402_damga_birakir(tmp_path: Path, monkeypatch) -> None:
    """Tahmin eksik kalsa bile (olculmemis fiyat) 402 ayni damgayi birakmali."""
    slug = _sahne(tmp_path, monkeypatch, bakiye=1700.0, uretim_stderr=GERCEK_402)
    assert gunluk.main(["--sehir", slug]) == 1
    damga = json.loads(gunluk.KREDI_BEKLIYOR.read_text(encoding="utf-8"))
    assert damga["sebep"] == "Kie 402" and damga["tarih"] == _bugun()


def test_baska_uretim_hatasi_damga_BIRAKMAZ(tmp_path: Path, monkeypatch) -> None:
    """Olusmus bir gorevin dusmesi telafiyi acarsa ayni gun iki kez para yanar."""
    slug = _sahne(tmp_path, monkeypatch, bakiye=5000.0,
                  uretim_stderr='Uretim basarisiz: {"state":"fail"}')
    assert gunluk.main(["--sehir", slug]) == 1
    assert not gunluk.KREDI_BEKLIYOR.exists()


# ----------------------------------------------------------------------
# telafi kapisi
# ----------------------------------------------------------------------
def _damga(tarih: str, sebep: str = "Kie 402") -> None:
    gunluk.KREDI_BEKLIYOR.write_text(
        json.dumps({"tarih": tarih, "sebep": sebep}), encoding="utf-8")


def test_telafi_damga_yoksa_calismaz() -> None:
    assert gunluk.telafi_karari([], _bugun())[0] is False


def test_telafi_dunku_damgayla_calismaz() -> None:
    _damga("2000-01-01")
    assert gunluk.telafi_karari([], _bugun())[0] is False


def test_telafi_bozuk_damgayla_calismaz() -> None:
    gunluk.KREDI_BEKLIYOR.write_text("{ json degil", encoding="utf-8")
    assert gunluk.telafi_karari([], _bugun())[0] is False


def test_telafi_bugunku_damga_ve_yayin_yokken_calisir() -> None:
    _damga(_bugun())
    calis, gerekce = gunluk.telafi_karari([], _bugun())
    assert calis is True and "Kie 402" in gerekce


def test_telafi_bugun_yayin_varken_calismaz(monkeypatch) -> None:
    """Elle telafi edilmis gunu ikinci kez uretmesin, sabah kaydini ezmesin."""
    _damga(_bugun())
    monkeypatch.setattr(gunluk, "bugunku_basarili", lambda g, b: [{"ts": b}])
    assert gunluk.telafi_karari([{"x": 1}], _bugun())[0] is False


def test_telafi_kapisi_stdoutta_yalniz_cikti_satiri_basar(monkeypatch, capsys) -> None:
    """stdout GITHUB_OUTPUT'a gidiyor; fazladan tek satir is akisini bozar."""
    _damga(_bugun())
    monkeypatch.setattr(gunluk, "defter", lambda: [])
    monkeypatch.setattr(gunluk, "kredi", lambda: pytest.fail("KREDI OKUNDU"))
    monkeypatch.setattr(gunluk, "kosa", lambda c, w: pytest.fail("SUBPROCESS CALISTI"))
    assert gunluk.main(["--telafi-kapisi"]) == 0
    assert capsys.readouterr().out == "calis=true\n"
