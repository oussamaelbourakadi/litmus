"""Run comparison and regression-verdict tests."""

from __future__ import annotations

from app.engine.compare import RunSummary, ThresholdConfig, compare_runs


def _summary(run_id: str, success_rate: float, rates: dict[str, float]) -> RunSummary:
    return RunSummary(
        run_id=run_id,
        success_rate=success_rate,
        latency_p50=0.0,
        latency_p95=0.0,
        total_cost=0.0,
        case_pass_rates=rates,
    )


def test_absolute_regression_is_detected() -> None:
    base = _summary("b", 1.0, {"c1": 1.0, "c2": 1.0})
    candidate = _summary("c", 0.5, {"c1": 1.0, "c2": 0.0})
    comparison = compare_runs(base, candidate)
    assert comparison.success_rate_delta == -0.5
    assert comparison.regressions == 1
    assert comparison.verdict.passed is False


def test_equal_runs_pass() -> None:
    base = _summary("b", 1.0, {"c1": 1.0})
    candidate = _summary("c", 1.0, {"c1": 1.0})
    comparison = compare_runs(base, candidate)
    assert comparison.regressions == 0
    assert comparison.verdict.passed is True


def test_improvement_passes() -> None:
    base = _summary("b", 0.5, {"c1": 0.0})
    candidate = _summary("c", 1.0, {"c1": 1.0})
    comparison = compare_runs(base, candidate)
    assert comparison.improvements == 1
    assert comparison.verdict.passed is True


def test_absolute_threshold_allows_small_drop() -> None:
    base = _summary("b", 1.0, {"c1": 1.0, "c2": 1.0})
    candidate = _summary("c", 0.9, {"c1": 1.0, "c2": 0.9})
    comparison = compare_runs(base, candidate, ThresholdConfig(mode="absolute", max_drop=0.2))
    assert comparison.verdict.passed is True


def test_relative_threshold() -> None:
    base = _summary("b", 0.8, {})
    candidate = _summary("c", 0.6, {})  # drop 0.2 -> relative 0.25
    assert compare_runs(base, candidate, ThresholdConfig("relative", 0.2)).verdict.passed is False
    assert compare_runs(base, candidate, ThresholdConfig("relative", 0.3)).verdict.passed is True


def test_added_and_removed_cases() -> None:
    base = _summary("b", 1.0, {"c1": 1.0})
    candidate = _summary("c", 1.0, {"c2": 1.0})
    statuses = {c.test_case_id: c.status for c in compare_runs(base, candidate).case_changes}
    assert statuses["c1"] == "removed"
    assert statuses["c2"] == "added"
