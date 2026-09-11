"""The measurement tool must never invent a plausible number.

`olc.py` shells out eight times (yt-dlp, ffprobe x2, ffmpeg x3, ...) and used
to check zero return codes. Most failures degrade honestly - a regex finds
nothing and the field becomes None. One does not:

    zamanlar = [...re.findall("pts_time:...", rs.stdout)]
    o["kesme_sayisi"] = len(zamanlar)

If that ffmpeg call fails, `zamanlar` is empty and the ledger records
**0 cuts** - a plausible, actionable, fabricated value. The brain then ranks
videos on it and tells a channel agent that the winning videos have no cuts.

`ses_var` had the same shape: a failed ffprobe meant "no audio", which then
explained away the missing LUFS as "this video is silent".
"""
import os
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "arac"
sys.path.insert(0, str(TOOLS))

import olc  # noqa: E402


class FakeRun:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


VIDEO_PROBE = (
    "width=1080\nheight=1920\nr_frame_rate=30/1\ncodec_name=h264\n"
    "duration=16.50\nsize=8000000\nbit_rate=4000000\n"
)
AUDIO_PROBE = "codec_name=aac\nchannels=2\nsample_rate=48000\n"
EBUR128 = "  I:         -14.2 LUFS\n  LRA:         6.1 LU\n  Peak:       -1.2 dBFS\n"
SCENES = "pts_time:1.20\npts_time:3.40\npts_time:7.10\n"


def fake_shell(monkeypatch, *, scene_rc=0, audio_rc=0, ebur_rc=0,
               scene_out=SCENES):
    """Replace olc.sh, routing by the command being run."""
    def _sh(args, timeout=600):
        joined = " ".join(str(a) for a in args)
        if args[0] == "ffprobe" and "a:0" in joined:
            return FakeRun(AUDIO_PROBE, "", audio_rc)
        if args[0] == "ffprobe":
            return FakeRun(VIDEO_PROBE, "", 0)
        if "ebur128" in joined:
            return FakeRun("", EBUR128, ebur_rc)
        if "scene" in joined:
            return FakeRun(scene_out, "ffmpeg patladi", scene_rc)
        return FakeRun()

    monkeypatch.setattr(olc, "sh", _sh)


# ─── the happy path still works ──────────────────────────────────────────────

def test_healthy_measurement(monkeypatch):
    fake_shell(monkeypatch)
    o = olc.olc("video.mp4")
    assert o["cozunurluk"] == "1080x1920" and o["fps"] == 30.0
    assert o["sure"] == 16.5
    assert o["ses_var"] is True
    assert o["lufs"] == -14.2 and o["true_peak"] == -1.2
    assert o["kesme_sayisi"] == 3
    assert o["kesme_per_10sn"] == round(3 / 16.5 * 10, 2)
    assert "hatalar" not in o


def test_genuinely_zero_cuts_is_still_zero(monkeypatch):
    """AImagine-Fear videolari gercekten 0 kesme iceriyor. Basarili bir
    olcumde sifir, sifir olarak kalmali , yoksa duzeltme gercek veriyi yer."""
    fake_shell(monkeypatch, scene_out="")
    o = olc.olc("video.mp4")
    assert o["kesme_sayisi"] == 0
    assert o["kesme_per_10sn"] == 0.0
    assert "hatalar" not in o


# ─── the fabricated zero ─────────────────────────────────────────────────────

def test_failed_scene_detection_does_not_report_zero_cuts(monkeypatch):
    fake_shell(monkeypatch, scene_rc=1, scene_out="")
    o = olc.olc("video.mp4")
    assert o["kesme_sayisi"] is None, "olculemeyen kesme sayisi 0 diye yazildi"
    assert o["kesme_per_10sn"] is None
    assert o["en_uzun_plan"] is None and o["ort_plan"] is None
    assert any("sahne tespiti" in h for h in o["hatalar"])


def test_failed_scene_detection_keeps_everything_measured_before_it(monkeypatch):
    """Erken donus, ondan ONCE olculmus alanlari dusurmemeli."""
    fake_shell(monkeypatch, scene_rc=1)
    o = olc.olc("video.mp4")
    assert o["cozunurluk"] == "1080x1920"
    assert o["sure"] == 16.5
    assert o["lufs"] == -14.2, "ses olcumu sahne hatasi yuzunden kayboldu"


# ─── the false "silent video" ────────────────────────────────────────────────

def test_failed_audio_probe_is_unknown_not_silent(monkeypatch):
    fake_shell(monkeypatch, audio_rc=1)
    o = olc.olc("video.mp4")
    assert o["ses_var"] is None, "ffprobe dustu ama video 'sessiz' ilan edildi"
    assert o["lufs"] is None
    assert any("ses akisi" in h for h in o["hatalar"])


def test_a_really_silent_video_is_still_reported_silent(monkeypatch):
    def _sh(args, timeout=600):
        joined = " ".join(str(a) for a in args)
        if args[0] == "ffprobe" and "a:0" in joined:
            return FakeRun("", "", 0)          # basarili, ama akis yok
        if args[0] == "ffprobe":
            return FakeRun(VIDEO_PROBE, "", 0)
        if "scene" in joined:
            return FakeRun(SCENES, "", 0)
        return FakeRun()

    monkeypatch.setattr(olc, "sh", _sh)
    o = olc.olc("video.mp4")
    assert o["ses_var"] is False, "gercekten sessiz video 'bilinmiyor' oldu"
    assert o["lufs"] is None
    assert "hatalar" not in o


def test_failed_loudness_pass_is_recorded(monkeypatch):
    fake_shell(monkeypatch, ebur_rc=1)
    o = olc.olc("video.mp4")
    # ebur128 patladi ama cikti yine de ayristirilabildiyse deger korunur;
    # ayristirilamadiysa hata kaydedilir. Burada cikti geliyor, yani deger var.
    assert o["lufs"] == -14.2


def test_failed_loudness_with_no_output_is_recorded(monkeypatch):
    def _sh(args, timeout=600):
        joined = " ".join(str(a) for a in args)
        if args[0] == "ffprobe" and "a:0" in joined:
            return FakeRun(AUDIO_PROBE, "", 0)
        if args[0] == "ffprobe":
            return FakeRun(VIDEO_PROBE, "", 0)
        if "ebur128" in joined:
            return FakeRun("", "", 1)          # patladi, cikti yok
        if "scene" in joined:
            return FakeRun(SCENES, "", 0)
        return FakeRun()

    monkeypatch.setattr(olc, "sh", _sh)
    o = olc.olc("video.mp4")
    assert o["lufs"] is None
    assert any("ses seviyesi" in h for h in o["hatalar"])


# ─── what the brain does with it ─────────────────────────────────────────────

def test_none_cut_count_does_not_become_a_target(monkeypatch, tmp_path):
    """Beyin, olculemeyen alani hedefe cevirmemeli."""
    import json
    sys.path.insert(0, str(ROOT))
    import beyin

    monkeypatch.chdir(tmp_path)
    folder = tmp_path / "kanallar" / "flashpoints"
    folder.mkdir(parents=True)
    rows = []
    for i in range(16):
        rows.append(json.dumps({
            "video_id": "v%03d" % i, "kanal": "flashpoints",
            "tarih": "2026-08-%02d" % (i + 1),
            "yayin_ts": "2026-08-%02dT10:00:00+00:00" % (i + 1),
            "baslik": "v%d" % i,
            "olcum": {"sure": 15.0 + i, "lufs": -14.0,
                      "kesme_per_10sn": None, "en_uzun_plan": None},
            "sonuc": {"izlenme": 100 + i * 10, "gecmis": []},
        }, ensure_ascii=False))
    (folder / "defter.jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")

    beyin.cmd_brain("flashpoints")
    metin = (folder / "BEYIN.md").read_text(encoding="utf-8")
    assert "kesme / 10 sn" not in metin.split("## 4.")[-1], \
        "olculemeyen kesme sayisi yine de hedef olarak verildi"
