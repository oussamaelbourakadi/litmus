"""MockProvider determinism and usage accounting."""

from __future__ import annotations

from app.providers.base import ProviderConfig
from app.providers.mock import MockProvider


async def test_same_prompt_and_seed_are_deterministic() -> None:
    provider = MockProvider()
    config = ProviderConfig(seed=42)
    first = await provider.generate("hello", config)
    second = await provider.generate("hello", config)
    assert first.text == second.text


async def test_different_seed_changes_output() -> None:
    provider = MockProvider()
    a = await provider.generate("hello", ProviderConfig(seed=1))
    b = await provider.generate("hello", ProviderConfig(seed=2))
    assert a.text != b.text


async def test_canned_response_is_returned() -> None:
    provider = MockProvider(responses={"ping": "pong"})
    result = await provider.generate("ping", ProviderConfig())
    assert result.text == "pong"
    assert result.usage.completion_tokens == 1


async def test_usage_counts_tokens() -> None:
    provider = MockProvider()
    result = await provider.generate("a b c", ProviderConfig(seed=0))
    assert result.usage.prompt_tokens == 3
    assert result.latency_ms == 0.0
