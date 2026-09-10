"""Galactic master wiring — AST guards and real-audio balance verification."""

from __future__ import annotations

import ast
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from core import ffmpeg_tools


class MasterWiringTest(unittest.TestCase):
    """AST guards for the four master_lufs-controlled wiring points in produce.py."""

    @classmethod
    def setUpClass(cls):
        produce_path = Path(__file__).resolve().parents[1] / "series" / "produce.py"
        cls.tree = ast.parse(produce_path.read_text(encoding="utf-8"))
        cls.produce_text = produce_path.read_text(encoding="utf-8")

    def test_master_audio_receives_the_bible_margin(self):
        calls = []
        for node in ast.walk(self.tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "master_audio"
            ):
                calls.append(node)

        self.assertEqual(len(calls), 1, "exactly one master_audio call expected")
        call = calls[0]

        kw_names = {kw.arg for kw in call.keywords}
        self.assertIn("true_peak_margin_db", kw_names, "missing true_peak_margin_db keyword")

        kw = next(kw for kw in call.keywords if kw.arg == "true_peak_margin_db")
        unparsed = ast.unparse(kw.value)
        self.assertIn(
            "master_true_peak_margin_db",
            unparsed,
            f"true_peak_margin_db must reference bible.master_true_peak_margin_db, got {unparsed}",
        )

    def test_voiceover_normalisation_is_tied_to_master_lufs(self):
        calls = []
        for node in ast.walk(self.tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "mix_voiceover"
            ):
                calls.append(node)

        self.assertEqual(len(calls), 1, "exactly one mix_voiceover call expected")
        call = calls[0]

        kw_names = {kw.arg for kw in call.keywords}
        self.assertIn("amix_normalize", kw_names, "missing amix_normalize keyword")

        kw = next(kw for kw in call.keywords if kw.arg == "amix_normalize")
        unparsed = ast.unparse(kw.value)
        self.assertIn(
            "master_lufs",
            unparsed,
            f"amix_normalize must reference master_lufs, got {unparsed}",
        )
        self.assertIn(
            "is None",
            unparsed,
            f"amix_normalize must check 'is None', got {unparsed}",
        )

    def test_music_bed_level_is_tied_to_master_lufs(self):
        expected_line = "music_volume = 0.50 if bible.master_lufs is not None else 0.28"
        self.assertIn(
            expected_line,
            self.produce_text,
            f"exact line not found: {expected_line}",
        )

    def test_mix_peak_limiting_is_tied_to_master_lufs(self):
        calls = []
        for node in ast.walk(self.tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "mix_background_music"
            ):
                calls.append(node)

        self.assertGreaterEqual(len(calls), 1, "at least one mix_background_music call expected")

        found = False
        for call in calls:
            kw_names = {kw.arg for kw in call.keywords}
            if "limit_mix_peak" in kw_names:
                kw = next(kw for kw in call.keywords if kw.arg == "limit_mix_peak")
                unparsed = ast.unparse(kw.value)
                if "master_lufs" in unparsed and "is not None" in unparsed:
                    found = True
                    break

        self.assertTrue(
            found,
            "no mix_background_music call has limit_mix_peak referencing master_lufs is not None",
        )


class NarrationSurvivesMasteringTest(unittest.TestCase):
    """Real-audio test: mastering must not change narration-to-music balance."""

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = Path(tempfile.mkdtemp(prefix="master_wiring_test_"))
        cls.addClassCleanup(shutil.rmtree, cls.tmpdir, ignore_errors=True)

    @staticmethod
    def _band_rms(path: Path, kind: str) -> float:
        """Return RMS level in dB for the given band."""
        if kind == "narration":
            filter_str = "highpass=f=700"
        elif kind == "music":
            filter_str = "lowpass=f=400"
        else:
            raise ValueError(f"unknown kind: {kind}")

        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-vn",
            "-af",
            f"{filter_str},astats=measure_overall=RMS_level:measure_perchannel=none",
            "-f",
            "null",
            "-",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        stderr = result.stderr
        matches = re.findall(r"RMS level dB:\s*([-\d.]+)", stderr)
        if not matches:
            raise RuntimeError(f"no RMS level found in ffmpeg output for {kind}: {stderr}")
        return float(matches[-1])

    def test_narration_to_music_ratio_survives_mastering(self):
        premix = self.tmpdir / "premix.mp4"
        mastered = self.tmpdir / "mastered.mp4"

        # Build the pre-mix: 1000 Hz narration at 1.0, 200 Hz music at 0.50
        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=1000:duration=6",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=200:duration=6",
            "-filter_complex",
            "[0:a]volume=1.0[v];[1:a]volume=0.50[m];[v][m]amix=inputs=2:normalize=0[a]",
            "-map",
            "[a]",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(premix),
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        # Measure ratio before mastering
        narr_before = self._band_rms(premix, "narration")
        music_before = self._band_rms(premix, "music")
        ratio_before = narr_before - music_before

        # Master the file
        ffmpeg_tools.master_audio(
            premix,
            mastered,
            target_i=-14.0,
            target_tp=-1.0,
            target_lra=11.0,
            true_peak_margin_db=0.2,
        )

        # Measure ratio after mastering
        narr_after = self._band_rms(mastered, "narration")
        music_after = self._band_rms(mastered, "music")
        ratio_after = narr_after - music_after

        # Assert balance preserved within 1.0 dB
        self.assertLessEqual(
            abs(ratio_after - ratio_before),
            1.0,
            f"narration/music ratio drifted: before={ratio_before:.2f} dB, after={ratio_after:.2f} dB",
        )

        # Assert mastered loudness within 1.0 LUFS of -14.0
        measured = ffmpeg_tools.measure_audio_loudness(mastered)
        self.assertIsNotNone(measured, "measure_audio_loudness returned None")
        loudness = measured["integrated_lufs"]
        self.assertLessEqual(
            abs(loudness - (-14.0)),
            1.0,
            f"mastered loudness {loudness:.1f} LUFS not within 1.0 of -14.0",
        )


if __name__ == "__main__":
    unittest.main()