"""Run metrics tests with hand-computed expectations."""

from __future__ import annotations

from app.engine.metrics import CaseOutcome, compute_metrics, estimate_cost, percentile


def _outcome(passed: bool, latency: float, *, repeat: int = 0, model: str = "mock") -> CaseOutcome:
    return CaseOutcome(
        passed=passed,
        latency_ms=latency,
        prompt_tokens=1,
        completion_tokens=1,
        evaluator_passed={"e": passed},
        model=model,
        repeat_index=repeat,
    )


def test_percentile_linear_interpolation() -> None:
    assert percentile([10, 20, 30, 40], 50) == 25.0
    assert percentile([10], 95) == 10.0


def test_estimate_cost_uses_price_table() -> None:
    # gpt-4o: 0.005 input + 0.015 output per 1k tokens.
    assert estimate_cost("gpt-4o", 1000, 1000) == 0.02
    assert estimate_cost("mock", 1000, 1000) == 0.0
    assert estimate_cost("unknown-model", 1000, 1000) == 0.0


def test_compute_metrics_basic() -> None:
    outcomes = [_outcome(True, 10.0), _outcome(False, 30.0)]
    metrics = compute_metrics(outcomes)
    assert metrics.total == 2
    assert metrics.passed == 1
    assert metrics.success_rate == 0.5
    assert metrics.evaluator_pass_rates["e"] == 0.5
    assert metrics.latency_mean == 20.0
    assert 0.0 <= metrics.success_rate_ci.low <= 0.5 <= metrics.success_rate_ci.high <= 1.0


def test_compute_metrics_repeats() -> None:
    outcomes = [
        _outcome(True, 5.0, repeat=0),
        _outcome(True, 5.0, repeat=1),
        _outcome(False, 5.0, repeat=2),
    ]
    metrics = compute_metrics(outcomes, repeats=3)
    assert metrics.repeat_success_mean is not None
    assert abs(metrics.repeat_success_mean - (2 / 3)) < 1e-9
    assert metrics.repeat_success_std is not None


def test_compute_metrics_empty() -> None:
    metrics = compute_metrics([])
    assert metrics.total == 0
    assert metrics.success_rate == 0.0
