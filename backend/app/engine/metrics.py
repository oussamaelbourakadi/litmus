"""Run metrics: success rate (+ bootstrap CI), latency percentiles, cost.

No metric is invented: every aggregate is computed from per-case outcomes, and
the aggregate success rate carries a bootstrap confidence interval.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from statistics import mean, pstdev

from app.engine.bootstrap import ConfidenceInterval, bootstrap_ci

# model -> (USD per 1k input tokens, USD per 1k output tokens). Extend as needed.
DEFAULT_PRICES: dict[str, tuple[float, float]] = {
    "mock": (0.0, 0.0),
    # Simulated demo prices for the scripted fixture provider.
    "mock-small": (0.0005, 0.0015),
    "mock-large": (0.01, 0.03),
    "gpt-4o": (0.005, 0.015),
    "gpt-4o-mini": (0.00015, 0.0006),
    "claude-3-5-sonnet": (0.003, 0.015),
    "mistral-small": (0.001, 0.003),
}


@dataclass(slots=True)
class CaseOutcome:
    """Minimal per-case signal needed to aggregate a run."""

    passed: bool
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    evaluator_passed: dict[str, bool]
    model: str
    repeat_index: int = 0
    errored: bool = False


@dataclass(slots=True)
class RunMetrics:
    total: int
    passed: int
    errors: int
    success_rate: float
    success_rate_ci: ConfidenceInterval
    latency_p50: float
    latency_p95: float
    latency_mean: float
    total_cost: float
    evaluator_pass_rates: dict[str, float] = field(default_factory=dict)
    repeat_success_mean: float | None = None
    repeat_success_std: float | None = None


def percentile(values: Sequence[float], q: float) -> float:
    """Linear-interpolation percentile (q in [0, 100])."""
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (q / 100.0) * (len(ordered) - 1)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    frac = rank - low
    return ordered[low] * (1.0 - frac) + ordered[high] * frac


def estimate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    prices: dict[str, tuple[float, float]] | None = None,
) -> float:
    table = prices if prices is not None else DEFAULT_PRICES
    input_price, output_price = table.get(model, (0.0, 0.0))
    return (prompt_tokens / 1000.0) * input_price + (completion_tokens / 1000.0) * output_price


def compute_metrics(
    outcomes: Sequence[CaseOutcome],
    *,
    repeats: int = 1,
    prices: dict[str, tuple[float, float]] | None = None,
    bootstrap_seed: int = 1234,
) -> RunMetrics:
    total = len(outcomes)
    if total == 0:
        empty_ci = bootstrap_ci([], seed=bootstrap_seed)
        return RunMetrics(0, 0, 0, 0.0, empty_ci, 0.0, 0.0, 0.0, 0.0)

    passed = sum(1 for o in outcomes if o.passed)
    errors = sum(1 for o in outcomes if o.errored)
    latencies = [o.latency_ms for o in outcomes]
    pass_flags = [1.0 if o.passed else 0.0 for o in outcomes]

    evaluator_names = {name for o in outcomes for name in o.evaluator_passed}
    evaluator_pass_rates: dict[str, float] = {}
    for name in sorted(evaluator_names):
        judged = [o.evaluator_passed[name] for o in outcomes if name in o.evaluator_passed]
        evaluator_pass_rates[name] = sum(1 for v in judged if v) / len(judged) if judged else 0.0

    total_cost = sum(
        estimate_cost(o.model, o.prompt_tokens, o.completion_tokens, prices) for o in outcomes
    )

    repeat_mean: float | None = None
    repeat_std: float | None = None
    if repeats > 1:
        by_repeat: dict[int, list[bool]] = {}
        for o in outcomes:
            by_repeat.setdefault(o.repeat_index, []).append(o.passed)
        per_repeat = [sum(1 for v in flags if v) / len(flags) for flags in by_repeat.values()]
        repeat_mean = mean(per_repeat)
        repeat_std = pstdev(per_repeat) if len(per_repeat) > 1 else 0.0

    return RunMetrics(
        total=total,
        passed=passed,
        errors=errors,
        success_rate=passed / total,
        success_rate_ci=bootstrap_ci(pass_flags, seed=bootstrap_seed),
        latency_p50=percentile(latencies, 50),
        latency_p95=percentile(latencies, 95),
        latency_mean=mean(latencies),
        total_cost=total_cost,
        evaluator_pass_rates=evaluator_pass_rates,
        repeat_success_mean=repeat_mean,
        repeat_success_std=repeat_std,
    )
