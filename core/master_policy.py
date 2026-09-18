"""Decision logic for the audio mastering retry loop.

This module provides a pure function that decides the next step in a mastering
loop based on measured true-peak and integrated loudness values.
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class MasterDecision:
    """Result of a mastering step decision.

    Attributes:
        action: One of "accept", "retry", or "stop".
        limiter_db: The next limiter ceiling in dB, only when action == "retry".
        reason: Empty string when action == "accept"; otherwise a human-readable
            diagnosis explaining the decision.
        gain_db: The next cumulative pre-limiter makeup gain in dB, only when
            action == "retry". The true-peak branch carries the current gain
            through unchanged; the loudness branch is the one that moves it.
    """
    action: str                 # "accept" | "retry" | "stop"
    limiter_db: float | None    # the next limiter ceiling, only when action == "retry"
    reason: str                 # "" when accept; a human-readable diagnosis otherwise
    gain_db: float | None = None   # next pre-limiter makeup gain, only when "retry"


def next_master_step(
    *,
    attempt: int,
    max_attempts: int,
    limiter_db: float,
    target_tp: float,
    target_i: float,
    measured_tp: float,
    measured_lufs: float,
    margin: float = 0.2,
    min_step: float = 0.3,
    max_total_reduction: float = 3.0,
    lufs_tolerance: float = 1.0,
    gain_db: float = 0.0,
    max_total_gain: float = 2.0,
) -> MasterDecision:
    """Decide the next mastering step based on measured audio metrics.

    Args:
        attempt: Current attempt number (1-indexed).
        max_attempts: Maximum number of attempts allowed.
        limiter_db: Current limiter ceiling in dB.
        target_tp: Target true-peak ceiling in dB.
        target_i: Target integrated loudness in LUFS.
        measured_tp: Measured true-peak of the current attempt in dB.
        measured_lufs: Measured integrated loudness of the current attempt in LUFS.
        margin: Safety margin added to overshoot when computing step (default 0.2 dB).
        min_step: Minimum step size when reducing limiter (default 0.3 dB).
        max_total_reduction: Maximum total reduction from target_tp allowed (default 3.0 dB).
        lufs_tolerance: Tolerance window around target_i for loudness gate (default 1.0 LU).
        gain_db: Pre-limiter makeup gain already applied, in dB (default 0.0).
        max_total_gain: Absolute bound on that makeup gain, in dB (default 2.0).
            A nudge is a legitimate lever; a shove buys loudness with limiter
            distortion, so anything larger is treated as a broken premaster.

    Returns:
        A MasterDecision with action, next limiter_db (if retry), and reason.
    """
    # Guard: reject non-finite measurements immediately (fail closed)
    if not math.isfinite(measured_tp):
        return MasterDecision(
            action="stop",
            limiter_db=None,
            reason=f"Measured true-peak is not finite: {measured_tp!r}.",
        )
    if not math.isfinite(measured_lufs):
        return MasterDecision(
            action="stop",
            limiter_db=None,
            reason=f"Measured integrated loudness is not finite: {measured_lufs!r}.",
        )

    # Small tolerance for floating-point boundary comparisons
    EPS = 1e-9

    # Gate 1: True-peak ceiling
    tp_ok = measured_tp <= target_tp + EPS

    # Gate 2: Integrated loudness window
    lufs_ok = abs(measured_lufs - target_i) <= lufs_tolerance + EPS

    # Rule 2: Both gates pass -> accept
    if tp_ok and lufs_ok:
        return MasterDecision(action="accept", limiter_db=None, reason="")

    # Rule 3: True-peak gate fails -> compute step and retry or stop
    if not tp_ok:
        overshoot = measured_tp - target_tp
        step = max(overshoot + margin, min_step)
        candidate = limiter_db - step
        floor = target_tp - max_total_reduction

        # Candidate strictly below floor -> stop (cumulative bound exceeded)
        if candidate < floor - EPS:
            return MasterDecision(
                action="stop",
                limiter_db=None,
                reason=(
                    f"Cumulative reduction bound exceeded: candidate ceiling {candidate:.2f} dB "
                    f"is below floor {floor:.2f} dB (target_tp={target_tp:.2f} - "
                    f"max_total_reduction={max_total_reduction:.2f}). "
                    f"Measured TP={measured_tp:.2f} dB, LUFS={measured_lufs:.2f}."
                ),
            )

        # Attempts exhausted -> stop
        if attempt >= max_attempts:
            return MasterDecision(
                action="stop",
                limiter_db=None,
                reason=(
                    f"Max attempts ({max_attempts}) exhausted. "
                    f"Measured TP={measured_tp:.2f} dB, LUFS={measured_lufs:.2f}."
                ),
            )

        # Otherwise retry with the candidate ceiling
        return MasterDecision(
            action="retry",
            limiter_db=candidate,
            reason=(
                f"True-peak overshoot {overshoot:.2f} dB > 0. "
                f"Step = max({overshoot:.2f} + {margin:.2f}, {min_step:.2f}) = {step:.2f} dB. "
                f"Next limiter ceiling = {candidate:.2f} dB."
            ),
            gain_db=gain_db,
        )

    # Rule 4: TP passes but loudness fails.
    #
    # Lowering the limiter is still the wrong lever: it produces a byte-identical
    # encode, which is the defect this module was written to kill. But it is not
    # the ONLY lever. Pre-limiter makeup gain moves integrated loudness directly,
    # and the limiter downstream is exactly what holds the peaks it creates under
    # the ceiling. So a SMALL miss is recoverable, and refusing to recover it
    # throws away a paid-for episode over a fraction of a decibel nobody can hear.
    # (2026-09-17, wild-encounter Part 11: LUFS -15.40 against a [-15, -13]
    # window. 0.40 LU killed the run after the Kie credits were already spent.)
    #
    # The bound is what keeps this honest. Past max_total_gain the premaster is
    # not slightly off, it is wrong, and shoving that much into a limiter buys
    # loudness with audible distortion. That still stops.
    window_lo = target_i - lufs_tolerance
    window_hi = target_i + lufs_tolerance
    shortfall = target_i - measured_lufs       # > 0 too quiet, < 0 too loud
    candidate_gain = gain_db + shortfall

    if abs(shortfall) > max_total_gain + EPS:
        return MasterDecision(
            action="stop",
            limiter_db=None,
            reason=(
                f"True-peak gate passed ({measured_tp:.2f} <= {target_tp:.2f}) but "
                f"loudness gate failed: measured LUFS={measured_lufs:.2f} is outside "
                f"target window [{window_lo:.2f}, {window_hi:.2f}]. "
                f"The {abs(shortfall):.2f} dB correction needed exceeds the "
                f"{max_total_gain:.2f} dB makeup bound; this is a broken premaster, "
                f"not a mastering nudge."
            ),
        )

    if abs(candidate_gain) > max_total_gain + EPS:
        return MasterDecision(
            action="stop",
            limiter_db=None,
            reason=(
                f"Cumulative makeup gain bound exceeded: candidate gain "
                f"{candidate_gain:.2f} dB is outside the {max_total_gain:.2f} dB bound "
                f"(already applied {gain_db:.2f} dB). "
                f"Measured TP={measured_tp:.2f} dB, LUFS={measured_lufs:.2f}."
            ),
        )

    if attempt >= max_attempts:
        return MasterDecision(
            action="stop",
            limiter_db=None,
            reason=(
                f"Max attempts ({max_attempts}) exhausted with loudness still outside "
                f"[{window_lo:.2f}, {window_hi:.2f}]. "
                f"Measured TP={measured_tp:.2f} dB, LUFS={measured_lufs:.2f}."
            ),
        )

    return MasterDecision(
        action="retry",
        limiter_db=limiter_db,
        reason=(
            f"True-peak gate passed ({measured_tp:.2f} <= {target_tp:.2f}) but "
            f"loudness gate failed: measured LUFS={measured_lufs:.2f} is outside "
            f"target window [{window_lo:.2f}, {window_hi:.2f}]. "
            f"Applying {shortfall:+.2f} dB of pre-limiter makeup gain "
            f"({gain_db:+.2f} to {candidate_gain:+.2f} dB); the limiter still holds "
            f"the ceiling at {limiter_db:.2f} dB."
        ),
        gain_db=candidate_gain,
    )
