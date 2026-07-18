"""Regression verdict tests."""

from __future__ import annotations

from litmus.compare import compare
from litmus.models import Threshold


def test_regression_fails() -> None:
    result = compare(1.0, 0.5, Threshold())
    assert result.passed is False
    assert result.delta == -0.5


def test_within_absolute_threshold_passes() -> None:
    assert compare(1.0, 0.9, Threshold(mode="absolute", max_drop=0.2)).passed is True


def test_relative_threshold() -> None:
    assert compare(0.8, 0.6, Threshold("relative", 0.2)).passed is False
    assert compare(0.8, 0.6, Threshold("relative", 0.3)).passed is True


def test_improvement_passes() -> None:
    assert compare(0.5, 1.0, Threshold()).passed is True
