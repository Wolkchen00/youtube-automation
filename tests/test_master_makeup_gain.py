"""The loudness lever and the loudness floor: two outages, measured.

2026-09-17, wild-encounter Part 11. Fully produced, Kie credits already spent,
then discarded by the master contract:

    True-peak gate passed (-1.20 <= -1.00) but loudness gate failed:
    measured LUFS=-15.40 is outside target window [-15.00, -13.00].
    Lowering the limiter cannot recover integrated loudness.

The first clause was right and the conclusion did not follow. Lowering the
LIMITER cannot move integrated loudness. Raising the gain BEFORE the limiter
can, and the limiter is precisely what holds the peaks that gain creates under
the ceiling. The channel went dark over 0.40 LU.

2026-09-18, the same episode, second attempt. The makeup lever was in by then
and it STILL failed, because the first cut of it refused any correction larger
than its own bound instead of spending what the bound allowed:

    The 2.10 dB correction needed exceeds the 2.00 dB makeup bound.

Refusing 2.10 because the budget is 2.00 throws the episode away rather than
getting 2.00 dB closer. Clamping instead of refusing would have saved both runs.

Then the measurement that settled what the real defect was. The raw shot audio
sits at -27.1 LUFS with 3.0 dB of peak headroom, and an explicit gain sweep
through the delivery limiter showed integrated loudness ASYMPTOTING:

    +11 dB -> -17.9    +13 dB -> -17.4    +15 dB -> -17.0    +17 dB -> -16.6

Seventeen decibels in, fourteen decibels of limiting, and still 2.6 LU short of
the window. The target is not merely hard for this material, it is unreachable
at any gain. A contract the material cannot meet is not a quality standard; it
is a coin flip that discards work already paid for.

So the policy now has two levers and a floor. These tests pin all three, and
the wiring tests read the numbers back out of the emitted ffmpeg filter string,
because a gain applied AFTER the limiter would be clipped straight off again
and a mock would never notice.
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
BOUND = 2.0


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


# ------------------------------------------------- the two outages, verbatim

def test_the_2026_09_17_numbers_no_longer_kill_the_episode():
    """Run 35277534367, attempt 2, exactly as the telemetry recorded it."""
    d = step(measured_tp=-1.20, measured_lufs=-15.40, limiter_db=-1.30)
    assert d.action == "retry", "0.40 LU must not be fatal after the credits are spent"
    assert d.gain_db == pytest.approx(1.40, abs=1e-9)
    assert d.limiter_db == pytest.approx(-1.30), (
        "the loudness lever must not also move the ceiling: true-peak already passed"
    )


def test_the_2026_09_18_numbers_spend_the_bound_instead_of_refusing_it():
    """Run 35374552727, attempt 2. The regression this test exists for.

    2.10 dB needed against a 2.00 dB bound. The first cut of the lever called
    that a broken premaster and stopped. Being 0.10 dB over budget is not a
    broken premaster; it is a reason to spend the budget.
    """
    d = step(measured_tp=-1.30, measured_lufs=-16.10, limiter_db=-1.80)
    assert d.action == "retry", "a correction over budget must still spend the budget"
    assert d.gain_db == pytest.approx(BOUND), "spend the bound, all of it, and no more"
    assert "bound allows only" in d.reason, (
        "a clamped correction must say so, or the log hides why it is still short"
    )


# ----------------------------------------------------------- the lever itself

def test_too_quiet_asks_for_positive_gain():
    d = step(measured_tp=-1.4, measured_lufs=-15.5)
    assert d.action == "retry"
    assert d.gain_db == pytest.approx(1.5)


def test_too_loud_asks_for_negative_gain():
    """Above the window is equally a failure, and attenuation is the same lever."""
    d = step(measured_tp=-1.4, measured_lufs=-12.6)
    assert d.action == "retry"
    assert d.gain_db == pytest.approx(-1.4)


def test_gain_never_escapes_the_bound_however_the_chain_runs():
    """Walk every reachable retry chain and watch the bound."""
    for lufs in (-12.0, -13.5, -15.0, -16.5, -18.0, -21.0):
        limiter, gain = TP, 0.0
        for attempt in range(1, 4):
            d = step(measured_tp=-1.4, measured_lufs=lufs, attempt=attempt,
                     limiter_db=limiter, gain_db=gain)
            if d.action != "retry":
                break
            assert abs(d.gain_db) <= BOUND + 1e-9, (
                f"LUFS={lufs} attempt={attempt}: gain {d.gain_db} escaped the bound"
            )
            limiter, gain = d.limiter_db, d.gain_db


def test_a_retry_must_always_move_a_lever():
    """No byte-identical rerun, in any direction. The original contract."""
    for lufs in (-11.0, -12.6, -15.4, -17.0, -20.0):
        d = step(measured_tp=-1.4, measured_lufs=lufs)
        if d.action != "retry":
            continue
        moved = (d.limiter_db != pytest.approx(TP)) or (
            d.gain_db is not None and d.gain_db != pytest.approx(0.0)
        )
        assert moved, f"retry at LUFS={lufs} changes nothing"


# --------------------------------------------------- too loud stays a hard no

@pytest.mark.parametrize("lufs", [-11.0, -9.5])
def test_loudness_above_the_window_past_the_bound_still_stops(lufs):
    """Attenuation is exact and free, so a premaster still this hot is wrong."""
    d = step(measured_tp=-1.4, measured_lufs=lufs)
    assert d.action == "stop"
    assert d.limiter_db is None
    assert "ABOVE the window" in d.reason


def test_cumulative_attenuation_cannot_creep_past_the_bound():
    d = step(measured_tp=-1.4, measured_lufs=-12.5, gain_db=-1.0)
    assert d.action == "stop", "-1.0 plus -1.5 dB exceeds the 2.0 dB bound"
    assert d.limiter_db is None


# ------------------------------------------------------------------ the floor

def test_without_a_floor_unreachable_loudness_is_still_fatal():
    """Default behaviour is unchanged: series that never opt in keep the old gate."""
    d = step(measured_tp=-1.4, measured_lufs=-17.5, gain_db=BOUND)
    assert d.action == "stop"
    assert "no loudness floor is configured" in d.reason


def test_with_a_floor_a_spent_lever_delivers_instead_of_discarding():
    d = step(measured_tp=-1.4, measured_lufs=-17.5, gain_db=BOUND, lufs_floor=-18.0)
    assert d.action == "accept", "above the floor with the lever spent must ship"
    assert d.reason, "a quiet delivery must never be silent about being quiet"
    assert "floor" in d.reason


def test_below_the_floor_still_stops():
    d = step(measured_tp=-1.4, measured_lufs=-19.0, gain_db=BOUND, lufs_floor=-18.0)
    assert d.action == "stop"
    assert "floor" in d.reason


def test_exactly_on_the_floor_counts_as_passing():
    d = step(measured_tp=-1.4, measured_lufs=-18.0, gain_db=BOUND, lufs_floor=-18.0)
    assert d.action == "accept"


def test_the_floor_never_short_circuits_the_lever():
    """The whole point: deliver as loud as the material honestly gets.

    A floor that accepted on sight would ship -17.0 when 2 dB of makeup gain
    was still unspent. The lever comes first; the floor only catches what is
    left over.
    """
    d = step(measured_tp=-1.4, measured_lufs=-17.0, gain_db=0.0, lufs_floor=-18.0)
    assert d.action == "retry", "unspent makeup gain must be spent before accepting quiet"
    assert d.gain_db == pytest.approx(BOUND)


def test_the_floor_applies_on_the_last_attempt_too():
    """No attempt left to spend the lever in, but the delivery is still good."""
    d = step(measured_tp=-1.4, measured_lufs=-17.0, attempt=3, max_attempts=3,
             lufs_floor=-18.0)
    assert d.action == "accept"


def test_the_floor_does_not_excuse_being_too_loud():
    """A floor is a floor. It says nothing about the ceiling."""
    d = step(measured_tp=-1.4, measured_lufs=-9.5, lufs_floor=-18.0)
    assert d.action == "stop"


# ----------------------------------------------------------- shared invariants

def test_accept_inside_the_window_carries_no_levers_and_no_reason():
    d = step(measured_tp=-1.4, measured_lufs=-14.2)
    assert d.action == "accept"
    assert d.limiter_db is None
    assert d.gain_db is None
    assert d.reason == ""


def test_true_peak_retry_carries_the_existing_gain_through_untouched():
    d = step(measured_tp=-0.5, measured_lufs=-14.0, gain_db=0.7)
    assert d.action == "retry"
    assert d.gain_db == pytest.approx(0.7), "the true-peak branch must not reset the gain"


def test_true_peak_still_takes_priority_when_both_gates_fail():
    d = step(measured_tp=-0.5, measured_lufs=-15.4)
    assert d.action == "retry"
    assert d.limiter_db < TP, "the ceiling is the first lever while true-peak is over"
    assert d.gain_db == pytest.approx(0.0)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_loudness_never_becomes_a_gain(bad):
    """A NaN gain would render a malformed filter string instead of failing loudly."""
    d = next_master_step(
        attempt=1, max_attempts=3, limiter_db=TP,
        target_tp=TP, target_i=LUFS,
        measured_tp=-1.5, measured_lufs=bad, lufs_floor=-18.0,
    )
    assert d.action == "stop"
    assert d.gain_db is None


# ------------------------------------------------------------------- wiring

class MakeupGainWiringTests(unittest.TestCase):
    """Read the levers back out of the real ffmpeg filter string."""

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

    def _run(self, measure, **kw):
        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=self._fake_run), \
             mock.patch.object(ffmpeg_tools, "measure_audio_loudness", side_effect=measure):
            return ffmpeg_tools.master_audio(
                self.src, self.out, target_i=-14.0, target_tp=-1.0, **kw
            )

    @staticmethod
    def _gain_db(chain: str) -> float:
        """Read volume= out of the chain and convert back to dB. 0.0 when absent."""
        found = re.search(r"volume=([0-9.]+)", chain)
        return 0.0 if not found else 20.0 * math.log10(float(found.group(1)))

    @staticmethod
    def _fixed(lufs, tp):
        return lambda _path: {"integrated_lufs": lufs, "true_peak_dbtp": tp}

    def _sequence(self, *readings):
        it = iter(readings)
        last = readings[-1]

        def measure(_path):
            return next(it, last)
        return measure

    def test_first_attempt_carries_no_gain(self):
        """A clean episode must emit the exact filter string it always emitted."""
        self._run(self._fixed(-14.0, -1.4))
        self.assertNotIn("volume=", self.filters[0])

    def test_a_quiet_first_attempt_produces_a_second_one_with_gain(self):
        self._run(self._sequence(
            {"integrated_lufs": -15.4, "true_peak_dbtp": -1.2},
            {"integrated_lufs": -14.1, "true_peak_dbtp": -1.3},
        ))
        self.assertEqual(len(self.filters), 2, "a recoverable miss must buy one more encode")
        self.assertAlmostEqual(self._gain_db(self.filters[1]), 1.4, places=3)

    def test_the_gain_sits_before_the_limiter(self):
        """The assertion the whole fix rests on.

        Gain applied after alimiter would be clipped straight back off, and the
        second attempt would measure the same loudness as the first: the exact
        byte-identical rerun the policy was built to prevent.
        """
        self._run(self._sequence(
            {"integrated_lufs": -15.4, "true_peak_dbtp": -1.2},
            {"integrated_lufs": -14.1, "true_peak_dbtp": -1.3},
        ))
        chain = self.filters[1]
        self.assertLess(
            chain.index("volume="), chain.index("alimiter="),
            "makeup gain must be applied BEFORE the limiter, or the limiter undoes it",
        )

    def test_an_over_budget_miss_still_spends_the_budget(self):
        """The 2026-09-18 shape, end to end through the real filter string."""
        self._run(self._sequence(
            {"integrated_lufs": -16.1, "true_peak_dbtp": -1.3},
            {"integrated_lufs": -14.4, "true_peak_dbtp": -1.3},
        ))
        self.assertEqual(len(self.filters), 2)
        self.assertAlmostEqual(self._gain_db(self.filters[1]), 2.0, places=3)

    def test_unreachable_loudness_without_a_floor_raises(self):
        with self.assertRaises(RuntimeError) as caught:
            self._run(self._fixed(-17.5, -1.4))
        self.assertIn("denemede", str(caught.exception))

    def test_unreachable_loudness_with_a_floor_delivers_the_master(self):
        result = self._run(self._fixed(-17.5, -1.4), lufs_floor=-18.0)
        self.assertTrue(pathlib.Path(result).exists())
        self.assertGreaterEqual(
            len(self.filters), 2, "the lever must be spent before the floor accepts"
        )
        self.assertAlmostEqual(self._gain_db(self.filters[-1]), 2.0, places=3)

    def test_a_floor_accept_leaves_telemetry_behind(self):
        """Shipping quiet is legitimate; shipping quiet SILENTLY is not."""
        self._run(self._fixed(-17.5, -1.4), lufs_floor=-18.0)
        written = list(self.logs.glob("master_attempts_*.json"))
        self.assertTrue(written, "a floor accept must leave evidence in logs/")
        self.assertIn("floor", written[0].read_text(encoding="utf-8"))

    def test_below_the_floor_still_raises(self):
        with self.assertRaises(RuntimeError) as caught:
            self._run(self._fixed(-22.0, -1.4), lufs_floor=-18.0)
        self.assertIn("floor", str(caught.exception))
