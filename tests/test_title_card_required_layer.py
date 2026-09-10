"""Title card required layer — fail-closed rendering and production call-site guard."""

from __future__ import annotations

import ast
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

from core import ffmpeg_tools


class TitleCardRequiredLayerTest(unittest.TestCase):
    """Tests for title_card_overlay required/preserve_case behaviour."""

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = Path(tempfile.mkdtemp(prefix="title_card_test_"))
        cls.src = cls.tmpdir / "src.mp4"
        # Create a 2s black video with silent audio
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "color=c=black:s=540x960:d=2",
                "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                "-shortest",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                str(cls.src),
            ],
            capture_output=True,
            check=True,
        )
        cls.addClassCleanup(shutil.rmtree, cls.tmpdir, ignore_errors=True)

    @staticmethod
    def _ink(video_path: Path) -> int:
        """Count bright pixels (>128) in upper third of frame at t=0.5s."""
        frame_raw = video_path.with_suffix(".raw")
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", "0.5",
                "-i", str(video_path),
                "-frames:v", "1",
                "-vf", "crop=540:320:0:60",
                "-pix_fmt", "gray",
                "-f", "rawvideo",
                str(frame_raw),
            ],
            capture_output=True,
            check=True,
        )
        data = frame_raw.read_bytes()
        frame_raw.unlink(missing_ok=True)
        return sum(1 for b in data if b > 128)

    def test_required_render_actually_draws_text(self):
        out = self.tmpdir / "titled.mp4"
        ffmpeg_tools.title_card_overlay(
            self.src, out,
            title="WASP-12b",
            subtitle="Its star is devouring it",
            duration=2.0,
            required=True,
            preserve_case=True,
        )
        self.assertTrue(out.exists() and out.stat().st_size > 0)
        ink = self._ink(out)
        self.assertGreaterEqual(ink, 200, f"expected >=200 bright pixels, got {ink}")

    def test_empty_title_card_draws_materially_less_ink(self):
        # First, render with text to get baseline ink
        out_text = self.tmpdir / "titled.mp4"
        ffmpeg_tools.title_card_overlay(
            self.src, out_text,
            title="WASP-12b",
            subtitle="Its star is devouring it",
            duration=2.0,
            required=True,
            preserve_case=True,
        )
        ink_text = self._ink(out_text)

        # Now render with empty title/subtitle and required=False (copy-through path)
        out_empty = self.tmpdir / "empty.mp4"
        ffmpeg_tools.title_card_overlay(
            self.src, out_empty,
            title="",
            subtitle="",
            duration=2.0,
            required=False,
            preserve_case=True,
        )
        ink_empty = self._ink(out_empty)

        self.assertLess(
            ink_empty,
            ink_text / 10,
            f"empty ink {ink_empty} not < 1/10 of text ink {ink_text}",
        )

    def test_required_true_rejects_empty_text(self):
        out = self.tmpdir / "fail.mp4"
        with self.assertRaises(RuntimeError):
            ffmpeg_tools.title_card_overlay(
                self.src, out,
                title="",
                subtitle="",
                duration=2.0,
                required=True,
                preserve_case=True,
            )

    def test_required_true_rejects_a_render_failure(self):
        out = self.tmpdir / "fail.mp4"
        with patch.object(ffmpeg_tools.subprocess, "run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "ffmpeg", stderr=b"boom"
            )
            with self.assertRaises(RuntimeError):
                ffmpeg_tools.title_card_overlay(
                    self.src, out,
                    title="WASP-12b",
                    subtitle="",
                    duration=2.0,
                    required=True,
                    preserve_case=True,
                )

    def test_required_false_still_falls_back_to_copy_through(self):
        out = self.tmpdir / "fallback.mp4"
        with patch.object(ffmpeg_tools.subprocess, "run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "ffmpeg", stderr=b"boom"
            )
            # Should NOT raise
            ffmpeg_tools.title_card_overlay(
                self.src, out,
                title="WASP-12b",
                subtitle="",
                duration=2.0,
                required=False,
                preserve_case=True,
            )
        self.assertTrue(out.exists() and out.stat().st_size > 0)

    def test_preserve_case_default_uppercases_and_opt_in_does_not(self):
        # Patch subprocess.run to capture the ffmpeg command
        recorded = {}

        def capture_run(cmd, *args, **kwargs):
            recorded["cmd"] = " ".join(cmd)
            # Return a mock CompletedProcess
            return Mock(returncode=0, stdout=b"", stderr=b"")

        with patch.object(ffmpeg_tools.subprocess, "run", side_effect=capture_run):
            # Default preserve_case=False -> should uppercase
            ffmpeg_tools.title_card_overlay(
                self.src, self.tmpdir / "default.mp4",
                title="WASP-12b",
                subtitle="",
                duration=2.0,
                required=False,
                preserve_case=False,
            )
            cmd_default = recorded.get("cmd", "")
            self.assertIn("WASP-12B", cmd_default, "default should uppercase title")

            recorded.clear()
            # preserve_case=True -> should keep original case
            ffmpeg_tools.title_card_overlay(
                self.src, self.tmpdir / "preserve.mp4",
                title="WASP-12b",
                subtitle="",
                duration=2.0,
                required=False,
                preserve_case=True,
            )
            cmd_preserve = recorded.get("cmd", "")
            self.assertIn("WASP-12b", cmd_preserve, "preserve_case=True should keep case")
            self.assertNotIn("WASP-12B", cmd_preserve, "preserve_case=True must not contain uppercased")

    def test_production_call_site_passes_the_required_and_preserve_case_flags(self):
        """Static AST guard: series/produce.py must call title_card_overlay with all required kwargs."""
        produce_path = Path(__file__).resolve().parents[1] / "series" / "produce.py"
        tree = ast.parse(produce_path.read_text(encoding="utf-8"))

        calls = []
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "title_card_overlay"
            ):
                calls.append(node)

        self.assertEqual(len(calls), 1, "exactly one title_card_overlay call expected")
        call = calls[0]

        kw_names = {kw.arg for kw in call.keywords}
        required_kws = {"required", "preserve_case", "duration", "title", "subtitle"}
        self.assertTrue(
            required_kws.issubset(kw_names),
            f"missing keyword arguments: {required_kws - kw_names}",
        )

        # Verify title and subtitle come from the plan card (not hardcoded)
        title_kw = next(kw for kw in call.keywords if kw.arg == "title")
        subtitle_kw = next(kw for kw in call.keywords if kw.arg == "subtitle")
        title_src = ast.unparse(title_kw.value)
        subtitle_src = ast.unparse(subtitle_kw.value)
        self.assertIn("title", title_src, "title kw value must reference plan 'title'")
        self.assertIn("subtitle", subtitle_src, "subtitle kw value must reference plan 'subtitle'")


if __name__ == "__main__":
    unittest.main()