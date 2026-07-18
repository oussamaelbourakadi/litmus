"""Bootstrap confidence interval tests."""

from __future__ import annotations

from app.engine.bootstrap import bootstrap_ci


def test_is_deterministic_with_seed() -> None:
    values = [1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0]
    a = bootstrap_ci(values, seed=42)
    b = bootstrap_ci(values, seed=42)
    assert (a.point, a.low, a.high) == (b.point, b.low, b.high)


def test_point_is_mean_and_within_interval() -> None:
    ci = bootstrap_ci([0.0, 1.0, 1.0, 0.0])
    assert ci.point == 0.5
    assert ci.low <= ci.point <= ci.high
    assert ci.low >= 0.0 and ci.high <= 1.0


def test_constant_values_have_zero_width() -> None:
    ci = bootstrap_ci([1.0, 1.0, 1.0])
    assert ci.point == 1.0
    assert ci.low == 1.0
    assert ci.high == 1.0


def test_empty_values() -> None:
    ci = bootstrap_ci([])
    assert ci.point == 0.0
    assert ci.low == 0.0
    assert ci.high == 0.0
