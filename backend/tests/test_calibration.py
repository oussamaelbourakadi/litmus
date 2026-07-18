"""Calibration utility tests."""

from __future__ import annotations

import pytest

from app.evaluators.base import EvalCase
from app.evaluators.calibration import cohen_kappa, judge_agreement
from app.evaluators.exact_match import ExactMatch


async def test_judge_agreement_perfect() -> None:
    evaluator = ExactMatch()
    cases = [
        (EvalCase(input="1", expected="a"), "a"),  # evaluator passes, label True
        (EvalCase(input="2", expected="b"), "x"),  # evaluator fails, label False
    ]
    labels = [True, False]
    assert await judge_agreement(evaluator, cases, labels) == 1.0


async def test_judge_agreement_half() -> None:
    evaluator = ExactMatch()
    cases = [
        (EvalCase(input="1", expected="a"), "a"),  # passes
        (EvalCase(input="2", expected="b"), "x"),  # fails
    ]
    labels = [True, True]  # human says both should pass
    assert await judge_agreement(evaluator, cases, labels) == 0.5


async def test_judge_agreement_length_mismatch() -> None:
    with pytest.raises(ValueError, match="same length"):
        await judge_agreement(ExactMatch(), [], [True])


def test_cohen_kappa_perfect_agreement() -> None:
    assert cohen_kappa([True, False, True, False], [True, False, True, False]) == 1.0


def test_cohen_kappa_no_agreement_beyond_chance() -> None:
    # Perfectly balanced but opposite labels -> kappa < 0.
    assert cohen_kappa([True, True, False, False], [False, False, True, True]) < 0.0


def test_cohen_kappa_length_mismatch() -> None:
    with pytest.raises(ValueError, match="same length"):
        cohen_kappa([True], [True, False])
