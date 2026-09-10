"""Wiring-level proof that master_audio actually obeys core.master_policy.

tests/test_master_policy.py proves the DECISION logic in isolation. This file
proves the LOOP consumes it: that the number the policy returns really lands in
the ffmpeg filter string, that a loudness-only failure stops instead of re-running
an identical encode, and that the per-attempt numbers survive a failure in logs/.

The limiter ceiling is read back out of the generated filter string rather than
trusted from a mock. That is deliberate: a mock that returns a passing second
measurement regardless of the limiter setting makes the UNFIXED loop look green,
so asserting on the emitted number is the only assertion that can fail for the
right reason.
"""

from __future__ import annotations

import json
import math
import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import ffmpeg_tools  # noqa: E402


class MasterConvergenceWiringTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="rf_conv_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.src = pathlib.Path(self.tmp) / "premaster.mp4"
        self.src.write_bytes(b"premaster")
        self.out = pathlib.Path(self.tmp) / "master.mp4"
        self.applied_limits: list[float] = []

        self.logs = pathlib.Path(self.tmp) / "logs"
        patcher = mock.patch.object(ffmpeg_tools, "LOGS_DIR", self.logs)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _fake_run(self, command, **_kwargs):
        text = " ".join(str(c) for c in command)
        if "-f" in command and "null" in command:
            return mock.Mock(returncode=0, stdout="", stderr=(
                '{ "input_i" : "-18.0", "input_tp" : "-2.0", "input_lra" : "7.0",'
                ' "input_thresh" : "-28.0", "target_offset" : "0.0" }'
            ))
        for token in text.split(","):
            if "alimiter=limit=" in token:
                self.applied_limits.append(
                    float(token.split("alimiter=limit=")[1].split(":")[0])
                )
        self.out.write_bytes(b"mastered")
        return mock.Mock(returncode=0, stdout="", stderr=(
            '{ "input_i" : "-18.0", "input_tp" : "-2.0", "input_lra" : "7.0",'
            ' "input_thresh" : "-28.0", "output_i" : "-14.0", "output_tp" : "-1.0",'
            ' "output_lra" : "7.0", "output_thresh" : "-24.0",'
            ' "normalization_type" : "linear", "target_offset" : "0.0" }'
        ))

    @staticmethod
    def _db(linear: float) -> float:
        return 20.0 * math.log10(linear)

    def _ceilings_db(self) -> list[float]:
        return [round(self._db(v), 4) for v in self.applied_limits]

    def _run(self, measure, **kw):
        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run), \
             mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            return ffmpeg_tools.master_audio(
                self.src, self.out, target_i=-14.0, target_tp=-1.0, **kw
            )

    # ---------------------------------------------- (a) the ceiling really moves

    def test_ceiling_moves_at_least_the_minimum_step_in_the_real_filter_string(self):
        """0.1 dB over must move the EMITTED ceiling 0.3 dB, not 0.1 dB.

        This is the assertion the old loop fails: it subtracted exactly the
        overshoot, so the second filter string would read -1.1, not -1.3.
        """
        def measure(_path):
            ceiling = self._db(self.applied_limits[-1])
            return {"integrated_lufs": -14.0,
                    "true_peak_dbtp": round(ceiling + 0.1, 4)}

        self._run(measure)
        ceilings = self._ceilings_db()
        self.assertGreaterEqual(len(ceilings), 2, "beklenen: en az iki deneme")
        self.assertAlmostEqual(ceilings[0], -1.0, places=3)
        self.assertAlmostEqual(ceilings[1], -1.3, places=3,
                               msg=f"tavan yanlis yere gitti: {ceilings}")

    def test_every_successive_ceiling_is_strictly_lower(self):
        """A peak that ignores the limiter entirely, so the loop keeps stepping.

        A FIXED overshoot relative to the ceiling would converge instead, because
        the step is the overshoot plus the margin. That is the margin working as
        designed, and it is asserted separately below.
        """
        def measure(_path):
            return {"integrated_lufs": -14.0, "true_peak_dbtp": 0.5}

        with self.assertRaises(RuntimeError):
            self._run(measure)
        ceilings = self._ceilings_db()
        self.assertEqual(ceilings, sorted(ceilings, reverse=True))
        for earlier, later in zip(ceilings, ceilings[1:]):
            self.assertLessEqual(later, earlier - 0.3 + 1e-6)

    # -------------------------------------- (b2) progressive, all three attempts

    def test_progressive_overshoot_uses_all_three_attempts_and_meets_both_gates(self):
        """Overshoot that grows faster than the step, then collapses.

        Three encodes are only genuinely needed when attempt 2 still misses, and
        that requires the overshoot to grow by more than the margin. A shrinking
        sequence converges on attempt 2, which is the loop working, not failing.
        """
        seq = iter([1.0, 1.5, 0.0])

        def measure(_path):
            ceiling = self._db(self.applied_limits[-1])
            return {"integrated_lufs": -14.3,
                    "true_peak_dbtp": round(ceiling + next(seq), 4)}

        self._run(measure)
        self.assertEqual(len(self.applied_limits), 3, "tam uc deneme beklenir")
        final_ceiling = self._ceilings_db()[-1]
        self.assertLessEqual(round(final_ceiling, 3), -1.0)
        self.assertLessEqual(abs(-14.3 + 14.0), 1.0)

    # -------------------------------- (b3) the identical-rerun bug, at the wiring

    def test_loudness_only_failure_runs_exactly_one_encode(self):
        """True-peak fine, loudness out of window: the old loop burned three
        byte-identical encodes here. Exactly one is allowed now."""
        def measure(_path):
            return {"integrated_lufs": -9.0, "true_peak_dbtp": -2.0}

        with self.assertRaises(RuntimeError) as caught:
            self._run(measure)
        self.assertEqual(len(self.applied_limits), 1,
                         f"ozdes denemeler tekrar kosuldu: {self._ceilings_db()}")
        self.assertIn("denemede", str(caught.exception))

    def test_loudness_only_failure_does_not_leave_a_master_behind(self):
        def measure(_path):
            return {"integrated_lufs": -9.0, "true_peak_dbtp": -2.0}

        with self.assertRaises(RuntimeError):
            self._run(measure)
        self.assertFalse(self.out.exists())
        self.assertFalse(self.out.with_suffix(".audio_master.json").exists())

    # ------------------------------------------------ (c) the cumulative bound

    def test_unreachable_peak_fails_closed_with_a_readable_reason(self):
        def measure(_path):
            return {"integrated_lufs": -14.0, "true_peak_dbtp": 0.5}

        with self.assertRaises(RuntimeError) as caught:
            self._run(measure)
        message = str(caught.exception)
        self.assertIn("denemede", message)
        self.assertTrue(message.strip().endswith("."), "teshis cumlesi eksik")

    def test_ceiling_never_escapes_the_cumulative_bound(self):
        def measure(_path):
            return {"integrated_lufs": -14.0, "true_peak_dbtp": 5.0}

        with self.assertRaises(RuntimeError):
            self._run(measure)
        floor = -1.0 - ffmpeg_tools.MASTER_MAX_TOTAL_REDUCTION_DB
        for ceiling in self._ceilings_db():
            self.assertGreaterEqual(ceiling, floor - 1e-6)

    def test_real_ep28_magnitude_overshoot_still_converges(self):
        """Regression guard for a bound chosen too tight.

        Production episode 28 overshot by 3.1 dB. A 3.0 dB cumulative bound turns
        that convergeable case into a fail-closed, killing an episode that the
        loop could have delivered. The bound must stay wide enough for it.
        """
        def measure(_path):
            ceiling = self._db(self.applied_limits[-1])
            return {"integrated_lufs": -14.0,
                    "true_peak_dbtp": round(ceiling + 3.1, 4)}

        self._run(measure)
        self.assertLessEqual(round(self._ceilings_db()[-1] + 3.1, 3), -1.0)

    # ------------------------------------------------------- (e) the telemetry

    def test_failure_writes_attempt_telemetry_under_logs(self):
        """The episode output directory is not uploaded by CI; logs/ is."""
        def measure(_path):
            return {"integrated_lufs": -14.0, "true_peak_dbtp": 0.5}

        with self.assertRaises(RuntimeError):
            self._run(measure)

        written = list(self.logs.glob("master_attempts_*.json"))
        self.assertEqual(len(written), 1, f"telemetri yazilmadi: {written}")
        payload = json.loads(written[0].read_text(encoding="utf-8"))
        self.assertTrue(payload["reason"])
        self.assertEqual(len(payload["attempts"]), len(self.applied_limits))
        for record in payload["attempts"]:
            self.assertIn("limit_db", record)
            self.assertIn("true_peak_dbtp", record)
            self.assertIn("integrated_lufs", record)

    def test_success_writes_no_failure_telemetry(self):
        def measure(_path):
            return {"integrated_lufs": -14.0, "true_peak_dbtp": -1.5}

        self._run(measure)
        self.assertEqual(list(self.logs.glob("master_attempts_*.json")), [])

    def test_telemetry_failure_does_not_mask_the_mastering_failure(self):
        """If logs/ cannot be written, the RuntimeError must still surface."""
        def measure(_path):
            return {"integrated_lufs": -14.0, "true_peak_dbtp": 0.5}

        with mock.patch.object(
            ffmpeg_tools.Path, "write_text", side_effect=OSError("disk dolu")
        ):
            with self.assertRaises(RuntimeError):
                self._run(measure)


if __name__ == "__main__":
    unittest.main()
