"""JsonSchema evaluator tests."""

from __future__ import annotations

from app.evaluators.base import EvalCase
from app.evaluators.json_schema import JsonSchema

_SCHEMA = {
    "type": "object",
    "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
    "required": ["name"],
}


async def test_conforming_json_passes() -> None:
    evaluator = JsonSchema(_SCHEMA)
    score = await evaluator.score(EvalCase(input="q"), '{"name": "Ada", "age": 36}')
    assert score.passed
    assert score.value == 1.0


async def test_invalid_json_fails() -> None:
    evaluator = JsonSchema(_SCHEMA)
    score = await evaluator.score(EvalCase(input="q"), "{not valid json")
    assert not score.passed
    assert score.reason is not None
    assert "JSON" in score.reason


async def test_non_conforming_json_fails() -> None:
    evaluator = JsonSchema(_SCHEMA)
    score = await evaluator.score(EvalCase(input="q"), '{"age": 36}')
    assert not score.passed
    assert score.reason is not None
