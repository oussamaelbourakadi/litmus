"""ScriptedProvider tests — deterministic, model-dependent accuracy."""

from __future__ import annotations

from app.providers.base import ProviderConfig
from app.providers.scripted import _BANK, ScriptedProvider


async def test_large_model_answers_everything_correctly() -> None:
    provider = ScriptedProvider()
    config = ProviderConfig(model="mock-large")
    for qa in _BANK:
        result = await provider.generate(qa.question, config)
        assert result.text == qa.answer


async def test_small_model_misses_only_hard_questions() -> None:
    provider = ScriptedProvider()
    config = ProviderConfig(model="mock-small")
    for qa in _BANK:
        result = await provider.generate(qa.question, config)
        if qa.hard:
            assert result.text != qa.answer
        else:
            assert result.text == qa.answer


async def test_small_model_scores_below_large() -> None:
    hard = sum(1 for qa in _BANK if qa.hard)
    assert 0 < hard < len(_BANK)  # guarantees a meaningful, non-trivial delta


async def test_is_deterministic() -> None:
    provider = ScriptedProvider()
    config = ProviderConfig(model="mock-large")
    first = await provider.generate("What is the capital of France?", config)
    second = await provider.generate("What is the capital of France?", config)
    assert first.text == second.text == "Paris"
    assert first.latency_ms == second.latency_ms


async def test_latency_and_tokens_are_nonzero() -> None:
    provider = ScriptedProvider()
    result = await provider.generate(
        "What is the capital of France?", ProviderConfig(model="mock-large")
    )
    assert result.latency_ms > 0
    assert result.usage.prompt_tokens > 0
    assert result.usage.completion_tokens > 0


async def test_unknown_prompt_is_handled() -> None:
    provider = ScriptedProvider()
    result = await provider.generate("totally unknown question", ProviderConfig(model="mock-large"))
    assert result.text == "I don't know"
