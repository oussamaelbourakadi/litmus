"""LLMJudge evaluator tests (deterministic via MockProvider)."""

from __future__ import annotations

from app.evaluators.base import EvalCase
from app.evaluators.llm_judge import LLMJudge
from app.providers.mock import MockProvider


async def test_parses_json_verdict_and_passes() -> None:
    provider = MockProvider(default='{"score": 0.9, "reason": "well argued"}')
    judge = LLMJudge(provider, rubric="Is the answer correct?", threshold=0.5)
    score = await judge.score(EvalCase(input="q", expected="Paris"), "Paris is the capital.")
    assert score.value == 0.9
    assert score.passed
    assert score.reason == "well argued"


async def test_below_threshold_fails() -> None:
    provider = MockProvider(default='{"score": 0.2, "reason": "weak"}')
    judge = LLMJudge(provider, rubric="x", threshold=0.5)
    score = await judge.score(EvalCase(input="q"), "answer")
    assert not score.passed


async def test_json_embedded_in_prose() -> None:
    provider = MockProvider(default='Here is my verdict: {"score": 1.0, "reason": "great"} done.')
    judge = LLMJudge(provider, rubric="x")
    score = await judge.score(EvalCase(input="q"), "answer")
    assert score.value == 1.0
    assert score.reason == "great"


async def test_float_fallback_when_no_json() -> None:
    provider = MockProvider(default="I would rate this 0.75 overall")
    judge = LLMJudge(provider, rubric="x")
    score = await judge.score(EvalCase(input="q"), "answer")
    assert score.value == 0.75


async def test_unparseable_yields_zero() -> None:
    provider = MockProvider(default="no numbers here")
    judge = LLMJudge(provider, rubric="x")
    score = await judge.score(EvalCase(input="q"), "answer")
    assert score.value == 0.0
    assert not score.passed
    assert score.reason is not None


async def test_score_is_clamped() -> None:
    provider = MockProvider(default='{"score": 1.8, "reason": "over"}')
    judge = LLMJudge(provider, rubric="x")
    score = await judge.score(EvalCase(input="q"), "answer")
    assert score.value == 1.0
