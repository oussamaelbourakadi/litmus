"""ExactMatch evaluator tests."""

from __future__ import annotations

from app.evaluators.base import EvalCase
from app.evaluators.exact_match import ExactMatch


async def test_case_insensitive_pass() -> None:
    evaluator = ExactMatch()
    score = await evaluator.score(EvalCase(input="q", expected="Paris"), "paris")
    assert score.passed
    assert score.value == 1.0


async def test_case_sensitive_fail() -> None:
    evaluator = ExactMatch(case_sensitive=True)
    score = await evaluator.score(EvalCase(input="q", expected="Paris"), "paris")
    assert not score.passed
    assert score.value == 0.0
    assert score.reason is not None


async def test_strip_whitespace() -> None:
    evaluator = ExactMatch()
    score = await evaluator.score(EvalCase(input="q", expected="yes"), "  YES  ")
    assert score.passed


async def test_missing_expected_fails() -> None:
    evaluator = ExactMatch()
    score = await evaluator.score(EvalCase(input="q"), "anything")
    assert not score.passed
