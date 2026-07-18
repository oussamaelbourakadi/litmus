"""Metrics: seeded bootstrap CI, latency percentiles, run summary.

Same statistical approach as the backend (percentile bootstrap, fixed seed) so
CLI and server results are comparable.
"""

from __future__ import annotations

import random
from collections.abc import Sequence

from litmus.models import CaseResult, RunResult


def bootstrap_ci(
    values: Sequence[float],
    *,
    resamples: int = 1000,
    confidence: float = 0.95,
    seed: int = 1234,
) -> tuple[float, float, float]:
    """Return (point, low, high) for the mean via a seeded percentile bootstrap."""
    if not values:
        return (0.0, 0.0, 0.0)
    point = sum(values) / len(values)
    rng = random.Random(seed)
    n = len(values)
    estimates: list[float] = []
    for _ in range(resamples):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        estimates.append(sum(sample) / n)
    estimates.sort()
    alpha = (1.0 - confidence) / 2.0
    low = estimates[int(alpha * resamples)]
    high = estimates[min(resamples - 1, int((1.0 - alpha) * resamples))]
    return (point, low, high)


def percentile(values: Sequence[float], q: float) -> float:
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


def summarize(results: list[CaseResult], *, seed: int = 1234) -> RunResult:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    errors = sum(1 for r in results if r.error is not None)
    latencies = [r.latency_ms for r in results]
    flags = [1.0 if r.passed else 0.0 for r in results]
    point, low, high = bootstrap_ci(flags, seed=seed)
    return RunResult(
        results=results,
        total=total,
        passed=passed,
        errors=errors,
        success_rate=point,
        ci_low=low,
        ci_high=high,
        latency_p50=percentile(latencies, 50),
        latency_p95=percentile(latencies, 95),
    )
