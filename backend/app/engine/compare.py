"""Compare two runs: aggregate deltas, per-case regressions, threshold verdict.

This is the primitive behind the CI gate (SDK / GitHub Action, 1.6): a candidate
run fails the gate when its success rate drops beyond the configured threshold.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RunSummary:
    """The comparable signal of a single run."""

    run_id: str
    success_rate: float
    latency_p50: float
    latency_p95: float
    total_cost: float
    case_pass_rates: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class ThresholdConfig:
    """Regression gate configuration.

    ``absolute``: fail if (base - candidate) success rate > ``max_drop``.
    ``relative``: fail if (base - candidate) / base > ``max_drop`` (base > 0).
    """

    mode: str = "absolute"
    max_drop: float = 0.0


@dataclass(slots=True)
class CaseChange:
    test_case_id: str
    base_pass_rate: float
    candidate_pass_rate: float
    status: str  # regressed | improved | unchanged | added | removed


@dataclass(slots=True)
class Verdict:
    passed: bool
    reason: str


@dataclass(slots=True)
class RunComparison:
    base_run_id: str
    candidate_run_id: str
    success_rate_base: float
    success_rate_candidate: float
    success_rate_delta: float
    latency_p50_delta: float
    latency_p95_delta: float
    cost_delta: float
    regressions: int
    improvements: int
    case_changes: list[CaseChange]
    verdict: Verdict


def _classify(base_rate: float | None, candidate_rate: float | None) -> str:
    if base_rate is None:
        return "added"
    if candidate_rate is None:
        return "removed"
    if candidate_rate < base_rate:
        return "regressed"
    if candidate_rate > base_rate:
        return "improved"
    return "unchanged"


def _verdict(base: float, candidate: float, threshold: ThresholdConfig) -> Verdict:
    drop = base - candidate
    if threshold.mode == "relative":
        relative = (drop / base) if base > 0 else 0.0
        failed = relative > threshold.max_drop
        detail = f"relative drop {relative:.4f} vs max {threshold.max_drop:.4f}"
    else:
        failed = drop > threshold.max_drop
        detail = f"absolute drop {drop:.4f} vs max {threshold.max_drop:.4f}"

    if failed:
        return Verdict(passed=False, reason=f"regression: {detail}")
    return Verdict(passed=True, reason=f"within threshold: {detail}")


def compare_runs(
    base: RunSummary, candidate: RunSummary, threshold: ThresholdConfig | None = None
) -> RunComparison:
    threshold = threshold or ThresholdConfig()

    case_ids = sorted(set(base.case_pass_rates) | set(candidate.case_pass_rates))
    changes: list[CaseChange] = []
    regressions = 0
    improvements = 0
    for case_id in case_ids:
        base_rate = base.case_pass_rates.get(case_id)
        candidate_rate = candidate.case_pass_rates.get(case_id)
        status = _classify(base_rate, candidate_rate)
        if status == "regressed":
            regressions += 1
        elif status == "improved":
            improvements += 1
        changes.append(
            CaseChange(
                test_case_id=case_id,
                base_pass_rate=base_rate if base_rate is not None else 0.0,
                candidate_pass_rate=candidate_rate if candidate_rate is not None else 0.0,
                status=status,
            )
        )

    return RunComparison(
        base_run_id=base.run_id,
        candidate_run_id=candidate.run_id,
        success_rate_base=base.success_rate,
        success_rate_candidate=candidate.success_rate,
        success_rate_delta=candidate.success_rate - base.success_rate,
        latency_p50_delta=candidate.latency_p50 - base.latency_p50,
        latency_p95_delta=candidate.latency_p95 - base.latency_p95,
        cost_delta=candidate.total_cost - base.total_cost,
        regressions=regressions,
        improvements=improvements,
        case_changes=changes,
        verdict=_verdict(base.success_rate, candidate.success_rate, threshold),
    )
