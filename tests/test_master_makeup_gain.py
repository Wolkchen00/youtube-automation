"""The loudness lever: a small LUFS miss must be recovered, not fatal.

Context, 2026-09-17. wild-encounter Part 11 was fully produced (Kie credits
already spent) and then thrown away by the master contract:

    True-peak gate passed (-1.20 <= -1.00) but loudness gate failed:
    measured LUFS=-15.40 is outside target window [-15.00, -13.00].
    Lowering the limiter cannot recover integrated loudness; further
    attempts would be byte-identical.

The first clause of that diagnosis was right and the conclusion did not follow.
Lowering the LIMITER cannot move integrated loudness. Raising the gain BEFORE
the limiter can, and the limiter is precisely what keeps the peaks that gain
creates under the ceiling. The channel went dark over 0.40 LU.

So these tests pin two things at once:

  * a small miss now buys one more encode with makeup gain applied, and
  * a large miss still stops, because shoving several dB into a limiter buys
    loudness with audible distortion. The bound is the whole reason this is a
    fix rather than a hole in the gate.

tests/test_master_policy.py owns the decision logic in isolation; the wiring
tests at the bottom read the number back out of the emitted ffmpeg filter
string, because a gain applied AFTER the limiter would be clipped straight back
off and a mock would never notice.
"""

from __future__ import annotations

import math
import pathlib
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import ffmpeg_tools  # noqa: E402
from core.master_policy import next_master_step  # noqa: E402


TP = -1.0
LUFS = -14.0


def step(**over):
    kwargs = dict(
        attempt=1,
        max_attempts=3,
        limiter_db=TP,
        target_tp=TP,
        target_i=LUFS,
        measured_tp=-1.5,
        measured_lufs=-14.0,
    )
    kwargs.update(over)
    return next_master_step(**kwargs)


# ------------------------------------------------- the outage, as a unit test

def test_the_exact_2026_09_17_numbers_no_longer_kill_the_episode():
    """The measurement that took sentinalihsandaily dark, verbatim."""
    d = step(measured_tp=-1.20, measured_lufs=-15.40, limiter_db=-1.30)
    assert d.action == "retry", "0.40 LU must not be fatal after the credits are spent"
    assert d.gain_db == pytest.approx(1.40, abs=1e-9), (
        "makeup gain must close exactly the measured gap to target"
    )
    assert d.limiter_db == pytest.approx(-1.30), (
        "the loudness lever must not also move the ceiling: true-peak already passed"
    )


def test_recovered_gain_would_land_inside_the_window():
    """Arithmetic sanity: applying the returned gain reaches the target."""
    d = step(measured_tp=-1.20, measured_lufs=-15.40)
    recovered = -15.40 + d.gain_db
    assert abs(recovered - LUFS) <= 1.0


# ----------------------------------------------------------- both directions

def test_too_quiet_asks_for_positive_gain():
    d = step(measured_tp=-1.4, measured_lufs=-15.5)
    assert d.action == "retry"
    assert d.gain_db > 0


def test_too_loud_asks_for_negative_gain():
    """Above the window is equally a failure, and attenuation is the same lever."""
    d = step(measured_tp=-1.4, measured_lufs=-12.6)
    assert d.action == "retry"
    assert d.gain_db < 0
    assert d.gain_db == pytest.approx(-1.4, abs=1e-9)


# ------------------------------------------------------------- the bound holds

@pytest.mark.parametrize("lufs", [-11.0, -17.0, -9.5, -20.0])
def test_a_large_miss_still_stops(lufs):
    """The cases the original policy was written for keep stopping.

    Every one of these needs 3 dB or more of correction. That is not a
    mastering nudge, it is a broken premaster, and it must not be papered over
    by driving a limiter.
    """
    d = step(measured_tp=-1.4, measured_lufs=lufs, attempt=1, max_attempts=3)
    assert d.action == "stop"
    assert d.limiter_db is None


def test_bound_is_exclusive_at_the_edge():
    """Exactly at the bound is still recoverable; a hair past it is not."""
    assert step(measured_tp=-1.4, measured_lufs=-16.0).action == "retry"
    assert step(measured_tp=-1.4, measured_lufs=-16.01).action == "stop"


def test_cumulative_gain_cannot_creep_past_the_bound():
    """Two legal-looking steps must not add up to an illegal one."""
    d = step(measured_tp=-1.4, measured_lufs=-15.2, gain_db=1.5)
    assert d.action == "stop", "1.5 + 1.2 dB exceeds the 2.0 dB makeup bound"
    assert "Cumulative makeup gain" in d.reason


def test_bound_is_configurable_and_respected():
    tight = step(measured_tp=-1.4, measured_lufs=-15.4, max_total_gain=1.0)
    assert tight.action == "stop"
    loose = step(measured_tp=-1.4, measured_lufs=-15.4, max_total_gain=3.0)
    assert loose.action == "retry"


# ------------------------------------------------------------ attempt budget

def test_loudness_retry_respects_the_attempt_budget():
    """No retry scheduled on the final attempt: there is nothing left to run."""
    d = step(measured_tp=-1.4, measured_lufs=-15.4, attempt=3, max_attempts=3)
    assert d.action == "stop"
    assert "Max attempts" in d.reason


# --------------------------------------------------- the two levers coexist

def test_true_peak_retry_carries_the_existing_gain_through_untouched():
    """A ceiling correction must not silently discard gain already applied."""
    d = step(measured_tp=-0.5, measured_lufs=-14.0, gain_db=0.7)
    assert d.action == "retry"
    assert d.gain_db == pytest.approx(0.7), "the true-peak branch must not reset the gain"


def test_true_peak_still_takes_priority_when_both_gates_fail():
    d = step(measured_tp=-0.5, measured_lufs=-15.4, gain_db=0.0)
    assert d.action == "retry"
    assert d.limiter_db < TP, "the ceiling is the first lever while true-peak is over"
    assert d.gain_db == pytest.approx(0.0)


def test_accept_carries_no_levers():
    d = step(measured_tp=-1.4, measured_lufs=-14.2)
    assert d.action == "accept"
    assert d.limiter_db is None
    assert d.gain_db is None


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_loudness_never_becomes_a_gain(bad):
    """A NaN gain would render a malformed filter string instead of failing loudly."""
    d = next_master_step(
        attempt=1, max_attempts=3, limiter_db=TP,
        target_tp=TP, target_i=LUFS,
        measured_tp=-1.5, measured_lufs=bad,
    )
    assert d.action == "stop"
    assert d.gain_db is None


# ------------------------------------------------------------------- wiring

class MakeupGainWiringTests(unittest.TestCase):
    """Read the gain back out of the real ffmpeg filter string."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="rf_makeup_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.src = pathlib.Path(self.tmp) / "premaster.mp4"
        self.src.write_bytes(b"premaster")
        self.out = pathlib.Path(self.tmp) / "master.mp4"
        self.filters: list[str] = []

        self.logs = pathlib.Path(self.tmp) / "logs"
        patcher = mock.patch.object(ffmpeg_tools, "LOGS_DIR", self.logs)
        patcher.start()
        self.addCleanup(patcher.stop)

    _REPORT = (
        '{ "input_i" : "-18.0", "input_tp" : "-2.0", "input_lra" : "7.0",'
        ' "input_thresh" : "-28.0", "output_i" : "-14.0", "output_tp" : "-1.0",'
        ' "output_lra" : "7.0", "output_thresh" : "-24.0",'
        ' "normalization_type" : "linear", "target_offset" : "0.0" }'
    )

    def _fake_run(self, command, **_kwargs):
        if "-f" in command and "null" in command:
            return mock.Mock(returncode=0, stdout="", stderr=(
                '{ "input_i" : "-18.0", "input_tp" : "-2.0", "input_lra" : "7.0",'
                ' "input_thresh" : "-28.0", "target_offset" : "0.0" }'
            ))
        self.filters.append(command[command.index("-af") + 1])
        self.out.write_bytes(b"mastered")
        return mock.Mock(returncode=0, stdout="", stderr=self._REPORT)

    def _run(self, measure):
        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run), \
             mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            return ffmpeg_tools.master_audio(
                self.src, self.out, target_i=-14.0, target_tp=-1.0
            )

    @staticmethod
    def _gain_db(chain: str) -> float:
        """Read volume= out of the chain and convert back to dB. 0.0 when absent."""
        found = re.search(r"volume=([0-9.]+)", chain)
        return 0.0 if not found else 20.0 * math.log10(float(found.group(1)))

    def test_first_attempt_carries_no_gain(self):
        """A clean episode must emit the exact filter string it always emitted."""
        self._run(lambda _p: {"integrated_lufs": -14.0, "true_peak_dbtp": -1.4})
        self.assertNotIn("volume=", self.filters[0])

    def test_a_quiet_first_attempt_produces_a_second_one_with_gain(self):
        calls = {"n": 0}

        def measure(_path):
            calls["n"] += 1
            if calls["n"] == 1:
                return {"integrated_lufs": -15.4, "true_peak_dbtp": -1.2}
            return {"integrated_lufs": -14.1, "true_peak_dbtp": -1.3}

        self._run(measure)
        self.assertEqual(len(self.filters), 2, "a recoverable miss must buy one more encode")
        self.assertAlmostEqual(self._gain_db(self.filters[1]), 1.4, places=3)

    def test_the_gain_sits_before_the_limiter(self):
        """The assertion the whole fix rests on.

        Gain applied after alimiter would be clipped straight back off, and the
        second attempt would measure the same loudness as the first: the exact
        byte-identical rerun this module was built to prevent.
        """
        calls = {"n": 0}

        def measure(_path):
            calls["n"] += 1
            if calls["n"] == 1:
                return {"integrated_lufs": -15.4, "true_peak_dbtp": -1.2}
            return {"integrated_lufs": -14.1, "true_peak_dbtp": -1.3}

        self._run(measure)
        chain = self.filters[1]
        self.assertLess(
            chain.index("volume="), chain.index("alimiter="),
            "makeup gain must be applied BEFORE the limiter, or the limiter undoes it",
        )

    def test_a_large_miss_never_reaches_a_second_encode(self):
        with self.assertRaises(RuntimeError) as caught:
            self._run(lambda _p: {"integrated_lufs": -19.0, "true_peak_dbtp": -1.4})
        self.assertEqual(len(self.filters), 1, "a broken premaster must not be driven louder")
        self.assertIn("broken premaster", str(caught.exception))
