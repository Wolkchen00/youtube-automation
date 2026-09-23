"""Caption sorusu ve kanalin ilk yorumu yayin aninda ekleniyor mu.

Rota dosyalari ve build.py dogrulayicilari DEGISMEZ: soru rotaya yazilmaz,
yayinla.py caption'i okuduktan sonra etiket satirinin ustune koyar. Yorum
Upload-Post first_comment alanina gider. Etiket sayisi ayni kalir.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parent.parent
YT_KOK = KOK.parent
if str(YT_KOK) not in sys.path:
    sys.path.insert(0, str(YT_KOK))

from series.engagement import valid_engagement_question  # noqa: E402


def _yayinla_kos(monkeypatch, tmp_path, caption_metni, ek_arg):
    yayinla = importlib.import_module("tools.yayinla")
    video = tmp_path / "m.mp4"
    video.write_bytes(b"x" * 1000)
    caption = tmp_path / "CAPTION.txt"
    caption.write_text(caption_metni, encoding="utf-8")
    monkeypatch.setattr(yayinla, "DEFTER", tmp_path / "yayin.jsonl")
    monkeypatch.setattr(yayinla, "defter_oku", lambda: [])
    alinan = []

    def _sahte_upload(**kw):
        alinan.append(kw)
        return {"success": True, "results": {kw["platform"]: {"success": True, "post_id": "XYZ"}}}

    monkeypatch.setattr(
        yayinla, "_yukleyici",
        lambda: (_sahte_upload, {"aimagine": "k"}, {"aimagine": ["youtube", "instagram", "tiktok"]}),
    )
    monkeypatch.setattr(sys, "argv", [
        "yayinla.py", str(video), "--caption-file", str(caption), "--title", "T #shorts",
    ] + ek_arg)
    assert yayinla.main() == 0
    return alinan


CAP = ("You're dropping past the CN Tower on a transparent slide above Toronto.\n\n"
       "#MegaSlideFear #CNTower #WaterSlide #POVReels #CGIAdventure")


def test_soru_etiketin_ustune_girer_yorum_her_platforma_gider(monkeypatch, tmp_path):
    alinan = _yayinla_kos(monkeypatch, tmp_path, CAP, [
        "--caption-question", "Would you ride this one?",
        "--first-comment", "Which city should we slide over next? 🌍",
    ])
    assert len(alinan) == 3
    for kw in alinan:
        satirlar = kw["social_caption"].splitlines()
        assert satirlar[-1].startswith("#MegaSlideFear")
        assert satirlar[-3] == "Would you ride this one?"
        assert kw["social_caption"].count("#") == 5
        assert kw["description"] == kw["social_caption"]
        assert kw["first_comment"] == "Which city should we slide over next? 🌍"


def test_argumansiz_yayin_bugunku_gibi(monkeypatch, tmp_path):
    alinan = _yayinla_kos(monkeypatch, tmp_path, CAP, [])
    for kw in alinan:
        assert kw["social_caption"] == CAP
        assert kw["first_comment"] == ""


def test_sorulu_captiona_ikinci_soru_eklenmez(monkeypatch, tmp_path):
    sorulu = CAP.replace("Toronto.", "Toronto. Ready?")
    alinan = _yayinla_kos(monkeypatch, tmp_path, sorulu, ["--caption-question", "Would you ride?"])
    assert alinan[0]["social_caption"] == sorulu


def test_gunluk_komutu_soru_ve_yorum_gecirir(monkeypatch, tmp_path):
    gunluk = importlib.import_module("tools.gunluk")
    out = tmp_path / "out" / "x"
    out.mkdir(parents=True)
    (out / "CAPTION.txt").write_text(CAP, encoding="utf-8")
    monkeypatch.setattr(gunluk, "KOK", tmp_path)
    monkeypatch.setattr(gunluk, "etkilesim_sec", lambda: ("Q one?", "C one?"))
    komut = gunluk._yayin_komutu(tmp_path / "m.mp4", "x", False, "T", "a,b")
    assert komut[komut.index("--caption-question") + 1] == "Q one?"
    assert komut[komut.index("--first-comment") + 1] == "C one?"


def test_etkilesim_dosyasi_yoksa_bos_doner(tmp_path):
    gunluk = importlib.import_module("tools.gunluk")
    assert gunluk.etkilesim_sec(5, tmp_path / "yok.json") == ("", "")


@pytest.mark.parametrize("icerik", ["{bozuk", "[]", '{"caption_questions": 5}', '""'])
def test_bozuk_etkilesim_dosyasi_yayini_durdurmaz(tmp_path, icerik):
    gunluk = importlib.import_module("tools.gunluk")
    yol = tmp_path / "e.json"
    yol.write_text(icerik, encoding="utf-8")
    soru, yorum = gunluk.etkilesim_sec(1, yol)
    assert isinstance(soru, str) and isinstance(yorum, str)


def test_gunler_arasinda_doner():
    gunluk = importlib.import_module("tools.gunluk")
    gorulen = {gunluk.etkilesim_sec(g) for g in range(8)}
    assert len(gorulen) == 8


def test_canli_etkilesim_havuzu_gecerli():
    veri = json.loads((KOK / "canon" / "ETKILESIM.json").read_text(encoding="utf-8"))
    for anahtar in ("caption_questions", "first_comments"):
        assert len(veri[anahtar]) >= 6
        for satir in veri[anahtar]:
            assert valid_engagement_question(satir), satir
            assert len(satir) <= 120, satir
            assert "subscribe" not in satir.lower(), satir
