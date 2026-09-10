"""Adversarial tests for core.master_policy.next_master_step.

Written independently of the implementation: the point is to break it, not to
confirm it. The three defects this policy replaces, for context:

  1. the old loop pulled the limiter down by exactly the overshoot, aiming at the
     boundary with no margin;
  2. when true-peak passed but loudness failed it changed nothing and re-ran a
     byte-identical attempt, burning two encodes on a guaranteed failure;
  3. it had no bound on how far the limiter could be pulled down.
"""

import math

import pytest

from core.master_policy import MasterDecision, next_master_step


TP = -1.0
LUFS = -14.0


def step(**over):
    """Call the policy with realistic defaults, overriding only what a test cares about."""
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


# ---------------------------------------------------------------- accept path

def test_accepts_when_both_gates_pass():
    d = step(measured_tp=-1.4, measured_lufs=-14.2)
    assert d.action == "accept"
    assert d.limiter_db is None
    assert d.reason == ""


def test_true_peak_exactly_on_target_counts_as_passing():
    """-1.0 <= -1.0. The old loop's `<=` agreed; a naive `<` rewrite would not."""
    d = step(measured_tp=TP, measured_lufs=LUFS)
    assert d.action == "accept"


@pytest.mark.parametrize("lufs", [-13.0, -15.0])
def test_loudness_exactly_on_window_edge_counts_as_passing(lufs):
    d = step(measured_tp=-1.2, measured_lufs=lufs)
    assert d.action == "accept"


# ------------------------------------------------------- the margin, by number

def test_small_overshoot_uses_the_minimum_step_not_the_overshoot():
    """The whole point of defect 1: 0.1 over must move 0.3, never 0.1.

    max(0.1 + 0.2, 0.3) == 0.3, so the ceiling lands at -1.3, not -1.1.
    """
    d = step(measured_tp=-0.9, limiter_db=-1.0)
    assert d.action == "retry"
    assert d.limiter_db == pytest.approx(-1.3, abs=1e-9)


def test_large_overshoot_uses_overshoot_plus_margin():
    """0.8 over: max(0.8 + 0.2, 0.3) == 1.0, so -1.0 becomes -2.0."""
    d = step(measured_tp=-0.2, limiter_db=-1.0)
    assert d.action == "retry"
    assert d.limiter_db == pytest.approx(-2.0, abs=1e-9)


def test_every_retry_moves_the_ceiling_strictly_down_by_at_least_min_step():
    """Drive the loop the way the caller will: feed each decision back in."""
    ceiling = TP
    seen = [ceiling]
    for attempt in range(1, 12):
        d = next_master_step(
            attempt=attempt, max_attempts=99, limiter_db=ceiling,
            target_tp=TP, target_i=LUFS,
            measured_tp=-0.95, measured_lufs=LUFS,
        )
        if d.action != "retry":
            break
        assert d.limiter_db < ceiling - 0.3 + 1e-9
        ceiling = d.limiter_db
        seen.append(ceiling)
    assert seen == sorted(seen, reverse=True), "ceilings must decrease monotonically"
    assert len(seen) > 1


# ------------------------------------------------------- the cumulative bound

def test_candidate_exactly_on_the_floor_is_allowed():
    """floor = -1.0 - 3.0 = -4.0. From -3.7 a 0.3 step lands exactly on it."""
    d = step(measured_tp=-0.95, limiter_db=-3.7, attempt=1, max_attempts=99)
    assert d.action == "retry"
    assert d.limiter_db == pytest.approx(-4.0, abs=1e-9)


def test_candidate_below_the_floor_stops_and_says_why():
    d = step(measured_tp=-0.95, limiter_db=-3.8, attempt=1, max_attempts=99)
    assert d.action == "stop"
    assert d.limiter_db is None
    assert d.reason, "a stop must carry a diagnosis"
    assert "-0.95" in d.reason or "0.95" in d.reason


def test_the_loop_cannot_run_forever_even_with_unlimited_attempts():
    """Termination proof: fixed floor plus a minimum step bounds the retries."""
    ceiling = TP
    for _ in range(500):
        d = next_master_step(
            attempt=1, max_attempts=10 ** 9, limiter_db=ceiling,
            target_tp=TP, target_i=LUFS,
            measured_tp=-0.5, measured_lufs=LUFS,
        )
        if d.action == "stop":
            break
        ceiling = d.limiter_db
    else:
        pytest.fail("policy never stopped: the cumulative bound does not terminate it")


def test_no_returned_ceiling_ever_sits_below_the_floor():
    floor = TP - 3.0
    for hundredths in range(0, 400):
        ceiling = TP - hundredths / 100.0
        d = next_master_step(
            attempt=1, max_attempts=99, limiter_db=ceiling,
            target_tp=TP, target_i=LUFS,
            measured_tp=-0.6, measured_lufs=LUFS,
        )
        if d.action == "retry":
            assert d.limiter_db >= floor - 1e-9, f"ceiling {d.limiter_db} escaped the floor"


# ------------------------------------------------ defect 2, the identical rerun

@pytest.mark.parametrize("lufs", [-11.0, -17.0, -9.5, -20.0])
def test_loudness_only_failure_stops_immediately_and_never_retries(lufs):
    """The defect this module exists to kill.

    True-peak passes, loudness does not. The limiter is the wrong lever, so a
    second attempt at the same ceiling would be byte-identical. Any "retry" here
    is the old bug wearing a new coat.
    """
    d = step(measured_tp=-1.4, measured_lufs=lufs, attempt=1, max_attempts=3)
    assert d.action == "stop", "loudness-only failure must never schedule another encode"
    assert d.limiter_db is None
    assert d.reason


def test_loudness_only_failure_stops_on_the_very_first_attempt():
    """Not on attempt 3 after two wasted encodes: on attempt 1."""
    d = step(measured_tp=-2.0, measured_lufs=-11.0, attempt=1, max_attempts=3)
    assert d.action == "stop"


# ------------------------------------------------------------ attempt budget

def test_last_attempt_stops_instead_of_retrying():
    d = step(measured_tp=-0.9, limiter_db=-1.0, attempt=3, max_attempts=3)
    assert d.action == "stop"
    assert d.limiter_db is None


def test_both_gates_failing_takes_the_true_peak_branch():
    """Rule priority: true-peak is actionable, loudness is not."""
    d = step(measured_tp=-0.5, measured_lufs=-11.0, attempt=1, max_attempts=3)
    assert d.action == "retry"
    assert d.limiter_db is not None


# ----------------------------------------------------------------- invariants

def test_retry_always_carries_a_float_ceiling():
    d = step(measured_tp=-0.9, limiter_db=-1.0)
    assert d.action == "retry"
    assert isinstance(d.limiter_db, float)
    assert math.isfinite(d.limiter_db)


def test_decision_is_immutable():
    d = step(measured_tp=-1.4, measured_lufs=-14.0)
    with pytest.raises(Exception):
        d.action = "retry"


def test_pure_function_same_inputs_same_result():
    a = step(measured_tp=-0.85, limiter_db=-1.2)
    b = step(measured_tp=-0.85, limiter_db=-1.2)
    assert a == b


# ------------------------------------------------- the trap Nemotron may miss

@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_measurement_never_yields_a_non_finite_ceiling(bad):
    """A NaN true-peak must not become a NaN limiter ceiling.

    The caller renders limiter_db into an ffmpeg filter string. A NaN there
    produces a silently malformed filter rather than a loud failure, so the
    policy must either stop or return a finite number, never propagate the NaN.
    """
    d = next_master_step(
        attempt=1, max_attempts=3, limiter_db=TP,
        target_tp=TP, target_i=LUFS,
        measured_tp=bad, measured_lufs=LUFS,
    )
    if d.action == "retry":
        assert math.isfinite(d.limiter_db), (
            f"non-finite measurement {bad} propagated into the limiter ceiling"
        )


@pytest.mark.parametrize("bad", [float("nan"), float("inf")])
def test_non_finite_loudness_does_not_silently_accept(bad):
    d = next_master_step(
        attempt=1, max_attempts=3, limiter_db=TP,
        target_tp=TP, target_i=LUFS,
        measured_tp=-1.5, measured_lufs=bad,
    )
    assert d.action != "accept", "a non-finite loudness reading must not pass the gate"


def test_returns_the_declared_type():
    assert isinstance(step(), MasterDecision)
