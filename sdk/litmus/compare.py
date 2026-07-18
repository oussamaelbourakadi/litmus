"""Regression verdict for the CI gate (scalar success-rate comparison)."""

from __future__ import annotations

from litmus.models import Comparison, Threshold


def compare(base_success: float, candidate_success: float, threshold: Threshold) -> Comparison:
    """Fail if the candidate's success rate drops beyond the threshold."""
    drop = base_success - candidate_success
    if threshold.mode == "relative":
        relative = (drop / base_success) if base_success > 0 else 0.0
        failed = relative > threshold.max_drop
        reason = f"relative drop {relative:.4f} vs max {threshold.max_drop:.4f}"
    else:
        failed = drop > threshold.max_drop
        reason = f"absolute drop {drop:.4f} vs max {threshold.max_drop:.4f}"

    prefix = "regression" if failed else "within threshold"
    return Comparison(
        base_success=base_success,
        candidate_success=candidate_success,
        delta=candidate_success - base_success,
        passed=not failed,
        reason=f"{prefix}: {reason}",
    )
