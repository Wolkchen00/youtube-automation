"""Takvim: hazir video gunleri uretim yapmaz, o gunun videosunu yayinlar.

2026-10-01 Ihsan karari: mevsim kapisi A/B testi icin 2 ve 3 Ekim'de iki hazir
video yayinlanacak, o iki gun otomasyon URETMEYECEK.
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


def _bugun() -> str:
    return datetime.now(gunluk.LA).strftime("%Y-%m-%d")


def _takvimli_kok(tmp_path: Path, tarih: str) -> Path:
    (tmp_path / "hazir").mkdir()
    (tmp_path / "hazir" / "v.mp4").write_bytes(b"video")
    (tmp_path / "hazir" / "v.caption.txt").write_text(
        "You're testing.\n\n#MegaSlideFear #Test", encoding="utf-8")
    (tmp_path / "hazir" / "takvim.json").write_text(json.dumps({"gunler": [{
        "tarih": tarih, "slug": "test-hazir", "video": "hazir/v.mp4",
        "caption": "hazir/v.caption.txt", "baslik": "Test drop #shorts",
    }]}), encoding="utf-8")
    return tmp_path


def _uretim_yasak(cmd, cwd):
    komut = " ".join(str(c) for c in cmd)
    if "yayinla.py" in komut:
        return gunluk.subprocess.CompletedProcess(cmd, 0, "ok", "")
    raise AssertionError("takvim gununde yayin disinda komut calisti: %s" % komut)


def test_takvim_gunu_uretmez_hazir_videoyu_yayinlar(tmp_path, monkeypatch) -> None:
    kok = _takvimli_kok(tmp_path, _bugun())
    monkeypatch.setattr(gunluk, "KOK", kok)
    monkeypatch.setattr(gunluk, "DEFTER", kok / "yayin.jsonl")
    cagrilar = []

    def _kosa(cmd, cwd):
        cagrilar.append([str(c) for c in cmd])
        return _uretim_yasak(cmd, cwd)

    monkeypatch.setattr(gunluk, "kosa", _kosa)
    monkeypatch.setattr(gunluk, "kredi", lambda: pytest.fail("takvim gunu kredi sorulmamali"))
    assert gunluk.main([]) == 0
    assert len(cagrilar) == 1
    komut = cagrilar[0]
    assert komut[komut.index("--title") + 1] == "Test drop #shorts"
    assert "--skip-if-published" in komut
    ek = json.loads(komut[komut.index("--ek-alanlar") + 1])
    assert ek == {"slug": "test-hazir", "kaynak": "takvim"}


def test_takvim_gunu_ayni_gun_kilidi_gecerli(tmp_path, monkeypatch) -> None:
    kok = _takvimli_kok(tmp_path, _bugun())
    monkeypatch.setattr(gunluk, "KOK", kok)
    monkeypatch.setattr(gunluk, "DEFTER", kok / "yayin.jsonl")
    monkeypatch.setattr(gunluk, "bugunku_basarili", lambda gecmis, bugun: [{"x": 1}])
    monkeypatch.setattr(gunluk, "kosa", lambda cmd, cwd: pytest.fail("yayin denenmemeli"))
    assert gunluk.main([]) == 0


def test_elle_sehir_verilince_takvim_atlanir(tmp_path, monkeypatch) -> None:
    kok = _takvimli_kok(tmp_path, _bugun())
    monkeypatch.setattr(gunluk, "KOK", kok)
    monkeypatch.setattr(gunluk, "takvim_yayinla",
                        lambda *a, **k: pytest.fail("--sehir verilince takvim kullanilmamali"))
    # Rota dosyasi yok, sure okunamaz ve kosu 1 ile durur: onemli olan takvime girmemesi.
    assert gunluk.main(["--sehir", "olmayan-rota"]) == 1


def test_takvimde_bugun_yoksa_none(tmp_path) -> None:
    kok = _takvimli_kok(tmp_path, "1999-01-01")
    assert gunluk.takvim_kaydi(_bugun(), kok / "hazir" / "takvim.json") is None


def test_takvim_dosyasi_yoksa_none(tmp_path) -> None:
    assert gunluk.takvim_kaydi(_bugun(), tmp_path / "yok.json") is None


def test_bozuk_takvim_sessizce_uretime_dusmez(tmp_path) -> None:
    yol = tmp_path / "takvim.json"
    yol.write_text("{bozuk", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        gunluk.takvim_kaydi(_bugun(), yol)


def test_eksik_dosyali_takvim_kaydi_yayinlamaz(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    monkeypatch.setattr(gunluk, "kosa", lambda cmd, cwd: pytest.fail("yayin denenmemeli"))
    kayit = {"tarih": _bugun(), "slug": "x", "video": "hazir/yok.mp4",
             "caption": "hazir/yok.txt", "baslik": "B #shorts"}
    assert gunluk.takvim_yayinla(kayit, [], _bugun(), False) == 1


def test_telafi_takvim_gununde_yayin_yoksa_calisir(tmp_path, monkeypatch, capsys) -> None:
    kok = _takvimli_kok(tmp_path, _bugun())
    monkeypatch.setattr(gunluk, "KOK", kok)
    monkeypatch.setattr(gunluk, "DEFTER", kok / "yayin.jsonl")
    assert gunluk.main(["--telafi-kapisi"]) == 0
    assert "calis=true" in capsys.readouterr().out


def test_gercek_takvimin_dosyalari_depoda() -> None:
    """Takvimdeki her kayit depoda gercekten var olan dosyalari gostermeli; yoksa
    o gun kanal karanlik kalir. Tarihler gecerli ve tekrarsiz olmali."""
    veri = json.loads((PROJE_KOKU / "hazir" / "takvim.json").read_text(encoding="utf-8"))
    tarihler = [k["tarih"] for k in veri["gunler"]]
    assert len(tarihler) == len(set(tarihler))
    for kayit in veri["gunler"]:
        datetime.strptime(kayit["tarih"], "%Y-%m-%d")
        assert (PROJE_KOKU / kayit["video"]).is_file(), kayit["video"]
        assert (PROJE_KOKU / kayit["caption"]).is_file(), kayit["caption"]
        assert kayit["baslik"].endswith("#shorts")
