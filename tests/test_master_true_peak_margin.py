"""Tests for true_peak_margin_db parameter in master_audio.

Models the sticky-floor measurement behavior where ffmpeg reports true peak
at 0.1 dB resolution and the encoder imposes a floor, causing the reported
value to stick while the ceiling walks down. When the ceiling goes low enough,
the true peak starts tracking again.
"""
from __future__ import annotations

import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import ffmpeg_tools  # noqa: E402


class TruePeakMarginTests(unittest.TestCase):
    """Tests for the true_peak_margin_db parameter."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tp_margin_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.src = pathlib.Path(self.tmp) / "premaster.mp4"
        self.src.write_bytes(b"premaster")
        self.out = pathlib.Path(self.tmp) / "master.mp4"
        self.applied_limits: list[float] = []
        self.input_paths: list[str] = []

    def _fake_run(self, command, **_kwargs):
        """Mock loudnorm measure pass + apply pass."""
        text = " ".join(str(c) for c in command)
        if "-f" in command and "null" in command:
            return mock.Mock(returncode=0, stdout="", stderr=(
                '{ "input_i" : "-18.0", "input_tp" : "-2.0", "input_lra" : "7.0",'
                ' "input_thresh" : "-28.0", "target_offset" : "0.0" }'
            ))
        # Apply pass: record limiter value and input path
        for token in text.split(","):
            if "alimiter=limit=" in token:
                self.applied_limits.append(
                    float(token.split("alimiter=limit=")[1].split(":")[0])
                )
        idx = command.index("-i")
        self.input_paths.append(str(command[idx + 1]))
        self.out.write_bytes(b"mastered")
        # Real loudnorm apply pass returns input_* AND output_* fields
        return mock.Mock(returncode=0, stdout="", stderr=(
            '{ "input_i" : "-18.0", "input_tp" : "-2.0", "input_lra" : "7.0",'
            ' "input_thresh" : "-28.0", "output_i" : "-14.0", "output_tp" : "-1.0",'
            ' "output_lra" : "7.0", "output_thresh" : "-24.0",'
            ' "normalization_type" : "linear", "target_offset" : "0.0" }'
        ))

    @staticmethod
    def _db(linear: float) -> float:
        import math
        return 20.0 * math.log10(linear)

    def test_sticky_floor_still_fails_with_the_legacy_zero_margin(self):
        """With margin 0.0 (default/omitted), ceiling walks -1.0, -1.1, -1.2 and fails."""
        STICKY_FLOOR_DBTP = -0.9

        def measure(path):
            limit_db = self._db(self.applied_limits[-1])
            tp = round(limit_db + 0.1, 1)
            return {"integrated_lufs": -14.0,
                    "true_peak_dbtp": max(STICKY_FLOOR_DBTP, tp)}

        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run), \
             mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            with self.assertRaises(RuntimeError):
                ffmpeg_tools.master_audio(self.src, self.out, target_i=-14.0, target_tp=-1.0)

        # Ceiling sequence in dB, rounded to 1 decimal
        ceilings_db = [round(self._db(lim), 1) for lim in self.applied_limits]
        self.assertEqual(ceilings_db, [-1.0, -1.1, -1.2])

    def test_margin_converges_on_the_same_signal(self):
        """With margin 0.2, ceiling walks -1.0 then -1.3 and passes on second attempt.

        The sticky floor at -0.9 only applies when ceiling is >= -1.2.
        When ceiling reaches -1.3, true peak tracks at ceiling + 0.1 = -1.2,
        which meets the -1.0 target.
        """
        STICKY_FLOOR_DBTP = -0.9
        STICKY_CEILING_THRESHOLD = -1.2  # below this, true peak tracks again

        def measure(path):
            limit_db = self._db(self.applied_limits[-1])
            tp = round(limit_db + 0.1, 1)
            if limit_db <= STICKY_CEILING_THRESHOLD:
                # Ceiling low enough: true peak tracks with 0.1 dB offset
                return {"integrated_lufs": -14.0, "true_peak_dbtp": tp}
            # Sticky region: floor at -0.9
            return {"integrated_lufs": -14.0,
                    "true_peak_dbtp": max(STICKY_FLOOR_DBTP, tp)}

        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run), \
             mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            ffmpeg_tools.master_audio(self.src, self.out, target_i=-14.0, target_tp=-1.0,
                                      true_peak_margin_db=0.2)

        self.assertLessEqual(len(self.applied_limits), 3, "at most 3 attempts")
        # Final delivered true peak computed same way as fake measurement
        last_limit_db = self._db(self.applied_limits[-1])
        if last_limit_db <= STICKY_CEILING_THRESHOLD:
            delivered_tp = round(last_limit_db + 0.1, 1)
        else:
            delivered_tp = max(STICKY_FLOOR_DBTP, round(last_limit_db + 0.1, 1))
        self.assertLessEqual(delivered_tp, -1.0)

    def test_margin_of_zero_is_identical_to_omitting_the_argument(self):
        """margin=0.0 and omitted argument produce identical ceiling sequences."""
        STICKY_FLOOR_DBTP = -0.9

        def measure(path):
            limit_db = self._db(self.applied_limits[-1])
            tp = round(limit_db + 0.1, 1)
            return {"integrated_lufs": -14.0,
                    "true_peak_dbtp": max(STICKY_FLOOR_DBTP, tp)}

        # Run with omitted argument
        self.applied_limits = []
        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run), \
             mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            with self.assertRaises(RuntimeError):
                ffmpeg_tools.master_audio(self.src, self.out, target_i=-14.0, target_tp=-1.0)
        seq_omitted = [round(self._db(lim), 1) for lim in self.applied_limits]

        # Run with explicit margin=0.0
        self.applied_limits = []
        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run), \
             mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            with self.assertRaises(RuntimeError):
                ffmpeg_tools.master_audio(self.src, self.out, target_i=-14.0, target_tp=-1.0,
                                          true_peak_margin_db=0.0)
        seq_explicit = [round(self._db(lim), 1) for lim in self.applied_limits]

        self.assertEqual(seq_omitted, seq_explicit)

    def test_margin_does_not_change_a_signal_that_passes_on_the_first_attempt(self):
        """Margin only takes effect after a FAILED attempt."""
        def measure(path):
            return {"integrated_lufs": -14.0, "true_peak_dbtp": -1.4}

        # Run with margin 0.0
        self.applied_limits = []
        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run), \
             mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            ffmpeg_tools.master_audio(self.src, self.out, target_i=-14.0, target_tp=-1.0,
                                      true_peak_margin_db=0.0)
        ceilings_0 = [round(self._db(lim), 1) for lim in self.applied_limits]

        # Run with margin 0.2
        self.applied_limits = []
        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run), \
             mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            ffmpeg_tools.master_audio(self.src, self.out, target_i=-14.0, target_tp=-1.0,
                                      true_peak_margin_db=0.2)
        ceilings_2 = [round(self._db(lim), 1) for lim in self.applied_limits]

        self.assertEqual(len(ceilings_0), 1, "exactly one ceiling with margin 0.0")
        self.assertEqual(len(ceilings_2), 1, "exactly one ceiling with margin 0.2")
        self.assertEqual(ceilings_0, ceilings_2, "ceilings must be equal on first-pass success")

    def test_loudness_side_of_the_contract_is_still_enforced(self):
        """Margin must not let a loud delivery through; LUFS failure raises with LUFS in message."""
        def measure(path):
            return {"integrated_lufs": -9.0, "true_peak_dbtp": -1.5}

        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run), \
             mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            with self.assertRaises(RuntimeError) as ctx:
                ffmpeg_tools.master_audio(self.src, self.out, target_i=-14.0, target_tp=-1.0,
                                          true_peak_margin_db=0.2)

        msg = str(ctx.exception).lower()
        self.assertIn("lufs", msg, f"error must mention LUFS: {ctx.exception!r}")


if __name__ == "__main__":
    unittest.main()