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
    """
    action: str                 # "accept" | "retry" | "stop"
    limiter_db: float | None    # the next limiter ceiling, only when action == "retry"
    reason: str                 # "" when accept; a human-readable diagnosis otherwise


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
        )

    # Rule 4: TP passes but loudness fails -> stop immediately, no retry
    # Lowering the limiter cannot move integrated loudness back into the window;
    # any further attempt would be byte-identical.
    return MasterDecision(
        action="stop",
        limiter_db=None,
        reason=(
            f"True-peak gate passed ({measured_tp:.2f} <= {target_tp:.2f}) but "
            f"loudness gate failed: measured LUFS={measured_lufs:.2f} is outside "
            f"target window [{target_i - lufs_tolerance:.2f}, {target_i + lufs_tolerance:.2f}]. "
            f"Lowering the limiter cannot recover integrated loudness; "
            f"further attempts would be byte-identical."
        ),
    )