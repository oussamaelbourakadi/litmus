"""Metrics and bootstrap tests."""

from __future__ import annotations

from litmus.metrics import bootstrap_ci, percentile, summarize
from litmus.models import CaseResult, Score


def test_bootstrap_is_deterministic() -> None:
    values = [1.0, 0.0, 1.0, 0.0]
    assert bootstrap_ci(values, seed=1) == bootstrap_ci(values, seed=1)


def test_bootstrap_point_is_mean() -> None:
    point, low, high = bootstrap_ci([0.0, 1.0, 1.0, 0.0])
    assert point == 0.5
    assert low <= point <= high


def test_percentile() -> None:
    assert percentile([10, 20, 30, 40], 50) == 25.0


def test_summarize() -> None:
    results = [
        CaseResult("a", "a", 5.0, True, [Score("e", 1.0, True)]),
        CaseResult("b", "x", 15.0, False, [Score("e", 0.0, False)]),
    ]
    run = summarize(results)
    assert run.total == 2
    assert run.passed == 1
    assert run.success_rate == 0.5
    assert run.latency_p50 == 10.0
