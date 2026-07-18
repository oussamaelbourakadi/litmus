"""Bootstrap confidence intervals — the statistical-rigor signature of Litmus.

Percentile bootstrap: resample the observations with replacement ``resamples``
times, recompute the statistic, and take empirical percentiles. Seeded, so every
reported interval is reproducible.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass


@dataclass(slots=True)
class ConfidenceInterval:
    point: float
    low: float
    high: float
    confidence: float


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def bootstrap_ci(
    values: Sequence[float],
    statistic: Callable[[Sequence[float]], float] = mean,
    *,
    resamples: int = 1000,
    confidence: float = 0.95,
    seed: int | None = 1234,
) -> ConfidenceInterval:
    """Return the point estimate and a ``confidence``-level bootstrap interval."""
    if not values:
        return ConfidenceInterval(0.0, 0.0, 0.0, confidence)

    point = statistic(values)
    n = len(values)
    rng = random.Random(seed)

    estimates: list[float] = []
    for _ in range(resamples):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        estimates.append(statistic(sample))
    estimates.sort()

    alpha = (1.0 - confidence) / 2.0
    low_index = int(alpha * resamples)
    high_index = min(resamples - 1, int((1.0 - alpha) * resamples))
    return ConfidenceInterval(point, estimates[low_index], estimates[high_index], confidence)
