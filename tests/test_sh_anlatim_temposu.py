"""Shadowed History anlatim temposu icin offline ffmpeg kanitlari."""

import json
import logging
import math
import pathlib
import re
import shutil
import subprocess
import sys

import pytest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import ffmpeg_tools
from core.narration import CHANNEL_NARRATION_CONFIG
from series.bible import Bible
from series.replenish import _build_prompt
from series.series_meta import SeriesMeta


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
FLASHPOINTS = REPO_ROOT / "shadowedhistory" / "flashpoints"


@pytest.fixture(autouse=True, scope="module")
def _ffmpeg_installed():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("ffmpeg and ffprobe are required")


def _run_ffmpeg(*args):
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", *map(str, args)],
        capture_output=True,
        check=True,
        timeout=60,
    )


def _make_video(path, duration):
    _run_ffmpeg(
        "-f", "lavfi", "-i", f"color=c=black:s=160x90:r=30:d={duration}",
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-t", str(duration), "-c:v", "mpeg4", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest", path,
    )


def _make_voice(path, duration):
    _run_ffmpeg(
        "-f", "lavfi", "-i",
        f"sine=frequency=660:duration={duration}:sample_rate=48000",
        "-c:a", "pcm_s16le", path,
    )


def _duration(path, stream=None):
    command = ["ffprobe", "-v", "error"]
    if stream:
        command.extend(["-select_streams", stream, "-show_entries", "stream=duration"])
    else:
        command.extend(["-show_entries", "format=duration"])
    command.extend(["-of", "csv=p=0", str(path)])
    result = subprocess.run(
        command, capture_output=True, check=True, text=True, timeout=30
    )
    return float(result.stdout.strip())


def test_kesme_yok_uzun_anlatim_tam_duyulur(tmp_path):
    # 12 sn video + 14 sn anlatim: uzatma tavanina (3 sn) DAYANMAYAN gercek vaka.
    # Ilk yazimda 3+6 sn secilmisti; o vaka tavana carpiyor ve "kesme yok" yerine
    # "tavan calisiyor" testine donusuyordu (Level 10 incelemesinde duzeltildi).
    video = tmp_path / "video_12s.mp4"
    voice = tmp_path / "voice_14s.wav"
    output = tmp_path / "mixed.mp4"
    _make_video(video, 12.0)
    _make_voice(voice, 14.0)

    result = ffmpeg_tools.mix_voiceover(video, voice, output)

    assert result == output
    konusma_sonu = 14.0 / ffmpeg_tools.NARRATION_MAX_TEMPO
    video_suresi = _duration(output, "v:0")
    ses_suresi = _duration(output, "a:0")
    # 1) konusma videonun ICINDE biter
    assert video_suresi >= konusma_sonu
    # 2) ses son karenin otesine tasmaz
    assert abs(video_suresi - ses_suresi) <= 0.15


def test_hizlandirma_tavani_1_05(tmp_path, monkeypatch):
    video = tmp_path / "video_3s.mp4"
    voice = tmp_path / "voice_6s.wav"
    output = tmp_path / "mixed.mp4"
    _make_video(video, 3.0)
    _make_voice(voice, 6.0)
    real_run = subprocess.run
    commands = []

    def recording_run(command, *args, **kwargs):
        commands.append(command)
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(ffmpeg_tools.subprocess, "run", recording_run)
    ffmpeg_tools.mix_voiceover(video, voice, output)

    ffmpeg_command = next(
        command for command in commands
        if command and command[0] == "ffmpeg" and "-filter_complex" in command
    )
    filter_graph = ffmpeg_command[ffmpeg_command.index("-filter_complex") + 1]
    tempos = [float(value) for value in re.findall(r"atempo=([0-9.]+)", filter_graph)]
    assert tempos
    assert max(tempos) <= ffmpeg_tools.NARRATION_MAX_TEMPO


def test_sigan_anlatim_tarihsel_komutu_korur(tmp_path, monkeypatch):
    video = tmp_path / "video_10s.mp4"
    voice = tmp_path / "voice_3s.wav"
    output = tmp_path / "mixed.mp4"
    _make_video(video, 10.0)
    _make_voice(voice, 3.0)
    real_run = subprocess.run
    commands = []

    def recording_run(command, *args, **kwargs):
        commands.append(command)
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(ffmpeg_tools.subprocess, "run", recording_run)
    ffmpeg_tools.mix_voiceover(video, voice, output)

    ffmpeg_command = next(
        command for command in commands
        if command and command[0] == "ffmpeg" and "-filter_complex" in command
    )
    filter_graph = ffmpeg_command[ffmpeg_command.index("-filter_complex") + 1]
    assert _duration(output) == pytest.approx(10.0, abs=0.2)
    assert "atempo" not in filter_graph
    assert "tpad" not in filter_graph
    assert "apad" not in filter_graph
    assert "duration=first" in filter_graph
    assert "-c:v" in ffmpeg_command
    assert ffmpeg_command[ffmpeg_command.index("-c:v") + 1] == "copy"
    assert "-shortest" in ffmpeg_command


def test_uzatma_tavani_ve_warning(tmp_path, caplog):
    video = tmp_path / "video_3s.mp4"
    voice = tmp_path / "voice_30s.wav"
    output = tmp_path / "mixed.mp4"
    _make_video(video, 3.0)
    _make_voice(voice, 30.0)

    with caplog.at_level(logging.WARNING, logger="youtube"):
        ffmpeg_tools.mix_voiceover(video, voice, output)

    assert _duration(output) <= 3.0 + ffmpeg_tools.NARRATION_MAX_EXTEND + 0.2
    assert any(record.levelno == logging.WARNING for record in caplog.records)
    assert "sonu kesilebilir" in caplog.text


def test_kelime_butcesi_ve_anlatimli_prompt_kurallari():
    series_data = json.loads(
        (FLASHPOINTS / "series.json").read_text(encoding="utf-8")
    )
    bible_data = json.loads(
        (FLASHPOINTS / "bible.json").read_text(encoding="utf-8")
    )
    cfg = series_data["auto_replenish"]
    micro_trim = float(bible_data["series"]["micro_trim"])
    speech_window = (
        cfg["shots"] * int(cfg["shot_seconds"])
        - cfg["shots"] * 2 * micro_trim
        - 0.7
    )
    limit = math.floor(speech_window * 2.05)
    assert cfg["narration"]["max_words"] <= limit

    _contents, instruction = _build_prompt(
        SeriesMeta(series_data), Bible(bible_data), cfg, 22, 1, []
    )
    assert "measured documentary pace of ~2 words per second" in instruction
    assert f"speaking window is {speech_window:.1f} seconds" in instruction
    assert "must end with a complete sentence" in instruction
    assert "ellipsis (\"...\")" in instruction
    assert "cliffhanger fragment" in instruction
    assert "Shot 2 directly continues shot 1's exact same moment and scene" in instruction
    assert "spoken sentence remains audibly unbroken across the cut" in instruction


def test_shadowedhistory_tts_talimati_ve_diger_kanallar():
    instruction = CHANNEL_NARRATION_CONFIG["shadowedhistory"]["instruction"]
    lowered = instruction.lower()
    assert "fast" not in lowered
    assert "pace tight" not in lowered
    assert "no long dramatic pauses" not in lowered
    assert "measured documentary pace" in lowered

    expected = {
        "galactic_experiment": (
            "Keep the voice warm and full of cosmic awe, but hold a tight pace for a roughly "
            "18-second video. Use one short pause only at the scale-reveal moment. "
            "State the claim itself in the first sentence and never let the delivery drag."
        ),
        "aimagine": None,
        "sentinal_ihsan": (
            "Speak in a calm, steady, first-person storyteller voice at NORMAL speaking volume ,  "
            "like a man matter-of-factly recounting something strange that happened on his night "
            "shift. Measured pace, grounded and confident, subtle tension in the pauses only. "
            "Do NOT whisper. No breathy or hushed delivery, no ASMR tone. Never shout either ,  "
            "just quiet, composed, natural speech."
        ),
        "sentinal_vlog": (
            "Speak like a real guy casually talking over a video he just shot on his phone ,  "
            "first person, relaxed, mildly amused, completely natural and fluent. Conversational "
            "pace with tiny human imperfections: a brief pause mid-thought, a small exhale or "
            "half-chuckle where it fits, throwaway words like 'okay so...' delivered off-the-cuff. "
            "He is talking to a friend, not to an audience. Absolutely NO announcer, documentary, "
            "salesman or ASMR tone; do NOT whisper, do not perform, do not over-enunciate. "
            "Just a normal dude who can't quite believe what his kitchen is doing right now."
        ),
    }
    assert {
        channel: CHANNEL_NARRATION_CONFIG[channel]["instruction"]
        for channel in expected
    } == expected


def test_kuyruktaki_planlar_10_saniye_part21_8_saniye():
    for number in range(22, 26):
        plan = json.loads(
            (FLASHPOINTS / "plans" / f"part{number:02d}.json").read_text(
                encoding="utf-8"
            )
        )
        assert all(shot["duration"] == "10" for shot in plan["shots"])

    part21 = json.loads(
        (FLASHPOINTS / "plans" / "part21.json").read_text(encoding="utf-8")
    )
    assert all(shot["duration"] == "8" for shot in part21["shots"])
