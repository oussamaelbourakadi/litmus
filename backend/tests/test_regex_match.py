"""RegexMatch evaluator tests."""

from __future__ import annotations

import re

from app.evaluators.base import EvalCase
from app.evaluators.regex_match import RegexMatch


async def test_pattern_found() -> None:
    evaluator = RegexMatch(r"\d{3}-\d{4}")
    score = await evaluator.score(EvalCase(input="q"), "call 123-4567 now")
    assert score.passed
    assert score.value == 1.0


async def test_pattern_not_found() -> None:
    evaluator = RegexMatch(r"^\d+$")
    score = await evaluator.score(EvalCase(input="q"), "abc")
    assert not score.passed
    assert score.reason is not None


async def test_flags_are_applied() -> None:
    evaluator = RegexMatch(r"hello", flags=re.IGNORECASE)
    score = await evaluator.score(EvalCase(input="q"), "HELLO world")
    assert score.passed
