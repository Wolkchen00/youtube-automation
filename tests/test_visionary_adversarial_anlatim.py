"""Visionary adversarial kontrolleri (Codex'in gormedigi vakalar).

Codex'in kendi testi konteyner suresine bakiyor. Konteyner suresi = max(video, ses),
yani ses videodan UZUN kalirsa test yine yesil yanar ama dosyanin sonunda goruntusuz
ses kuyrugu kalir. Burada VIDEO AKISI ile SES AKISI ayri ayri olculur.
"""

import json
import pathlib
import shutil
import subprocess
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import ffmpeg_tools
from series.bible import Bible
from series.replenish import _build_prompt
from series.series_meta import SeriesMeta

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True, scope="module")
def _ffmpeg_installed():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("ffmpeg ve ffprobe gerekli")


def _run(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, args)],
                   capture_output=True, check=True, timeout=120)


def _make_video(path, duration):
    _run("-f", "lavfi", "-i", f"color=c=black:s=160x90:r=30:d={duration}",
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-t", str(duration), "-c:v", "mpeg4", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-shortest", path)


def _make_voice(path, duration):
    _run("-f", "lavfi", "-i",
         f"sine=frequency=660:duration={duration}:sample_rate=48000",
         "-c:a", "pcm_s16le", path)


def _stream_duration(path, stream):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", stream,
         "-show_entries", "stream=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, check=True, text=True, timeout=30).stdout.strip()
    return float(out.splitlines()[0])


def _capture_cmd(monkeypatch, fn):
    real = subprocess.run
    seen = []

    def rec(cmd, *a, **kw):
        seen.append(cmd)
        return real(cmd, *a, **kw)

    monkeypatch.setattr(ffmpeg_tools.subprocess, "run", rec)
    fn()
    return next(c for c in seen if c and c[0] == "ffmpeg" and "-filter_complex" in c)


# A1: uretim gercegi - 19.0 sn video, 21.0 sn anlatim.
# Ses ve goruntu AYNI anda bitmeli; aksi halde son karenin otesinde sessiz ses kuyrugu kalir.
def test_A1_ses_ve_goruntu_ayni_anda_biter(tmp_path):
    video, voice, out = tmp_path / "v.mp4", tmp_path / "a.wav", tmp_path / "o.mp4"
    _make_video(video, 19.0)
    _make_voice(voice, 21.0)

    ffmpeg_tools.mix_voiceover(video, voice, out)

    v = _stream_duration(out, "v:0")
    a = _stream_duration(out, "a:0")
    assert abs(v - a) <= 0.15, (
        f"ses ve goruntu ayni anda bitmiyor: video {v:.2f}s / ses {a:.2f}s "
        f"-> son karenin otesinde {a - v:.2f}s goruntusuz ses kaliyor"
    )


# A2: A1 ile ayni kosu, ama asil vaadi olcer: konusma videonun ICINDE bitmeli.
def test_A2_konusma_video_bitmeden_biter(tmp_path):
    video, voice, out = tmp_path / "v.mp4", tmp_path / "a.wav", tmp_path / "o.mp4"
    _make_video(video, 19.0)
    _make_voice(voice, 21.0)

    ffmpeg_tools.mix_voiceover(video, voice, out)

    v = _stream_duration(out, "v:0")
    konusma_sonu = 21.0 / ffmpeg_tools.NARRATION_MAX_TEMPO
    assert v >= konusma_sonu, (
        f"konusma {konusma_sonu:.2f}s'de bitiyor ama video {v:.2f}s'de bitiyor -> KESILIYOR"
    )


# A3: hizlandirma tek basina yetiyorsa video uzatilmasin, gereksiz yeniden kodlama olmasin.
def test_A3_uzatma_gerekmiyorsa_video_kopyalanir(tmp_path, monkeypatch):
    video, voice, out = tmp_path / "v.mp4", tmp_path / "a.wav", tmp_path / "o.mp4"
    _make_video(video, 10.0)
    _make_voice(voice, 10.0)   # 1.042x hiz yeter, uzatmaya gerek yok

    cmd = _capture_cmd(monkeypatch, lambda: ffmpeg_tools.mix_voiceover(video, voice, out))
    fg = cmd[cmd.index("-filter_complex") + 1]

    assert "tpad" not in fg, f"uzatma gerekmiyorken tpad uygulandi: {fg}"
    assert cmd[cmd.index("-c:v") + 1] == "copy", (
        "uzatma gerekmiyorken video yeniden kodlandi (kalite kaybi)"
    )


# A4: shadowedhistory'ye ozel sureklilik kurali BASKA serilere sizmamali.
def test_A4_diger_anlatimli_seriler_etkilenmez():
    eh = REPO_ROOT / "galactic_experience" / "event-horizon"
    series_data = json.loads((eh / "series.json").read_text(encoding="utf-8"))
    bible_data = json.loads((eh / "bible.json").read_text(encoding="utf-8"))
    cfg = series_data["auto_replenish"]

    _c, instruction = _build_prompt(
        SeriesMeta(series_data), Bible(bible_data), cfg, 1, 1, []
    )

    assert "Shot 2 directly continues" not in instruction, (
        "3 cekimli event-horizon'a 'Shot 2 devam etsin' kurali sizmis"
    )
    assert "SCENE FLOW" in instruction, (
        "event-horizon kendi SCENE FLOW kuralini kaybetmis"
    )
