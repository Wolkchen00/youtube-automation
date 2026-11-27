"""MAGI-2 yolu (2026-11-27, Ihsan karari: kanal MAGI-2'ye gecti).

26 Kasim karsilastirmasinda MAGI-2 promptdaki "[2.0-4.0]" araligini ayri cekim
sayip tam 2,0 sn'de sicradi. Bu testler MAGI promptunun zaman izi tasimadigini,
kredi/model/olcu hesaplarinin MAGI'ye gore yapildigini ve eski Seedance yolunun
bozulmadigini kilitler.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

import build
import profil as profil_modulu
from tools import gunluk

KOK = Path(__file__).resolve().parent.parent


def _kapi_rotalari():
    return [
        yol for yol in build.discover_route_paths(KOK)
        if build.load_route(yol, KOK).konsept == "kapi"
    ]


def test_kapi_kanonu_magi_destekli_havuz_degil() -> None:
    assert build.magi_destekli(KOK, "kapi") is True
    assert build.magi_destekli(KOK, "havuz") is False


@pytest.mark.parametrize("yol", _kapi_rotalari(), ids=lambda y: y.stem)
def test_magi_promptu_zaman_izsiz_ve_sinirda(yol: Path) -> None:
    rota = build.load_route(yol, KOK)
    magi = build.magi_kanonu_yukle(KOK, "kapi")
    metin = build.render_magi(magi, rota, "magi2")
    assert build.magi_zaman_izleri(metin) == []
    assert len(metin) <= build.MAGI_PROMPT_TAVAN
    assert "<<" not in metin and ">>" not in metin
    assert "1080x1920" in metin
    # rotanin her vurusu sirayla, araliksiz tasinir
    for parca in build._aralik_metinleri(rota.sections["BEATS"]):
        assert parca.split(" ", 1)[1][:40] in metin
    assert build.validate_magi(rota, KOK, metin) == []


def test_zaman_izi_yakalanir() -> None:
    assert build.magi_zaman_izleri("[2.0-4.0] she sits") == ["[2.0-4.0]"]
    assert build.magi_zaman_izleri("from 4 to 6 seconds") != []
    assert build.magi_zaman_izleri("at about 2.0 seconds she sits") != []
    assert build.magi_zaman_izleri("Shot 2: the cloud") != []
    assert build.magi_zaman_izleri("a single continuous 15-second shot") == []


def test_magi_kredisi_ve_komutu() -> None:
    magi = profil_modulu.PROFILLER["magi2"]
    assert profil_modulu.profil_modeli(magi) == "magi-2"
    assert profil_modulu.profil_modeli(profil_modulu.PROFILLER["720p"]) == "bytedance/seedance-2"
    # 15 sn x 17,6 = 264; MIN_KREDI tabani korunur
    assert gunluk.gerekli_kredi("1080p", 15, "magi-2") == max(gunluk.MIN_KREDI, 264.0)
    assert gunluk.gerekli_kredi("1080p", 15) == 1530  # Seedance 1080p eskisi gibi
    komut = gunluk.uretim_komutu("slug", 15, magi, "https://x/y.jpg")
    assert komut[komut.index("--model") + 1] == "magi-2"
    assert komut[komut.index("--resolution") + 1] == "1080p"


def test_magi_ilk_kosu_kanaryadir(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(gunluk, "ONAY_DOSYASI", tmp_path / "yok.json")
    anahtar = profil_modulu.matris_anahtari("magi-2", 15, "1080p", 24)
    assert profil_modulu.YETENEK_MATRISI[anahtar] == "kanarya"
    izinli, durum = gunluk.yayin_izni("magi2", 15)
    assert izinli is False and "kanarya" in durum


def test_seedance_onayi_magi_yi_acmaz(monkeypatch, tmp_path) -> None:
    onay = tmp_path / "onay.json"
    onay.write_text(json.dumps({
        "model": "bytedance/seedance-2", "sure": 15, "cozunurluk": "1080p", "fps": 24,
        "master_sha": "a" * 64, "profil_hash": profil_modulu.profil_hash(),
        "olculen": {"genislik": 1080, "yukseklik": 1920, "fps": 24.0, "sure": 15.0},
    }), encoding="utf-8")
    monkeypatch.setattr(gunluk, "ONAY_DOSYASI", onay)
    izinli, _ = gunluk.yayin_izni("magi2", 15)
    assert izinli is False


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg yok")
def test_normalize_magi_olcusunu_kapiya_getirir(tmp_path) -> None:
    ham = tmp_path / "video" / "x_gunluk_01.mp4"
    ham.parent.mkdir()
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i", "testsrc2=size=1076x1928:rate=25:duration=2",
         "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(ham)],
        check=True,
    )
    cikti = gunluk.normalize_et(ham, profil_modulu.PROFILLER["magi2"])
    probe, hata = gunluk.ffprobe_json(cikti)
    assert hata is None
    olculen = gunluk.akis_olcumleri(probe)
    assert (olculen["genislik"], olculen["yukseklik"]) == (1080, 1920)
    assert abs(olculen["fps"] - 24) < 0.01
    assert olculen["ses_var"] is True
    assert "_gunluk_" in cikti.name and cikti.parent.name == "norm"


def test_magi_prompt_kapisi_eksik_dosyada_durur(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    assert gunluk.magi_prompt_sorunlari("olmayan")[0].startswith("PROMPT_MAGI.txt yok")
    hedef = tmp_path / "out" / "r" / "PROMPT_MAGI.txt"
    hedef.parent.mkdir(parents=True)
    hedef.write_text("[0.0-2.0] walk", encoding="utf-8")
    assert any("zaman izi" in s for s in gunluk.magi_prompt_sorunlari("r"))
