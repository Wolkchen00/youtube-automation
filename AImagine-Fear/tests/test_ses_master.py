from __future__ import annotations

import json
import subprocess
from pathlib import Path

from core.ffmpeg_tools import master_audio
from tools import gunluk


def _sidecar(path: Path, lufs=-14.0, peak=-1.1) -> None:
    path.with_suffix(".audio_master.json").write_text(
        json.dumps(
            {
                "delivery_limiter": {
                    "attempts": [
                        {"integrated_lufs": lufs, "true_peak_dbtp": peak}
                    ]
                }
            }
        ),
        encoding="utf-8",
    )


def test_real_ffmpeg_master_sidecar_meets_loudness_contract(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    master = tmp_path / "master" / "master.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "lavfi", "-i", "testsrc2=size=160x284:rate=24:duration=2",
            "-f", "lavfi", "-i", "sine=frequency=1000:duration=2",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(source),
        ],
        check=True,
        capture_output=True,
    )
    master_audio(source, master, target_i=-14.0, target_tp=-1.0)
    metadata = json.loads(master.with_suffix(".audio_master.json").read_text(encoding="utf-8"))
    delivered = metadata["delivery_limiter"]["attempts"][-1]
    assert abs(delivered["integrated_lufs"] - (-14.0)) <= 1.0
    assert delivered["true_peak_dbtp"] <= -1.0
    assert gunluk.ses_denetle(master) == []


def test_loudness_sidecar_missing_or_too_quiet_fails(tmp_path: Path) -> None:
    master = tmp_path / "master.mp4"
    master.write_bytes(b"master")
    assert "sidecar okunamadi" in gunluk.ses_denetle(master)[0]
    _sidecar(master, lufs=-30.0)
    assert any("-30.0 LUFS" in error for error in gunluk.ses_denetle(master))


def test_upload_size_limit_is_read_from_core(monkeypatch, tmp_path: Path) -> None:
    master = tmp_path / "master.mp4"
    master.write_bytes(b"x" * 32)
    _sidecar(master)
    monkeypatch.setitem(gunluk.PROFILLER["1080p"], "min_bayt", 1)
    monkeypatch.setattr(gunluk, "ffprobe_json", lambda path: ({
        "streams": [
            {"codec_type": "video", "width": 1080, "height": 1920, "r_frame_rate": "24/1"},
            {"codec_type": "audio", "r_frame_rate": "0/0"},
        ],
        "format": {"duration": "15.0"},
    }, None))
    from core import uploader

    monkeypatch.setattr(uploader, "MAX_UPLOAD_MB", 0.000001)
    errors, _ = gunluk.denetle(master, 15, gunluk.PROFILLER["1080p"])
    assert any("yukleme tavani" in error for error in errors)
