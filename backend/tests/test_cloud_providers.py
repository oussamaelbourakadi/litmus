"""Cloud providers: response parsing (mocked transport) and missing-key errors."""

from __future__ import annotations

import httpx
import pytest

from app.providers.anthropic import AnthropicProvider
from app.providers.base import ProviderConfig, ProviderError
from app.providers.mistral import MistralProvider
from app.providers.openai import OpenAIProvider


async def test_openai_parses_response() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "hi"}}],
                "usage": {"prompt_tokens": 2, "completion_tokens": 1},
            },
        )

    provider = OpenAIProvider(api_key="test-key", transport=httpx.MockTransport(handler))
    result = await provider.generate("q", ProviderConfig(model="gpt-4o", seed=1))
    assert result.text == "hi"
    assert result.usage.prompt_tokens == 2
    assert result.usage.completion_tokens == 1


async def test_openai_missing_key_raises() -> None:
    provider = OpenAIProvider(api_key=None)
    with pytest.raises(ProviderError, match="OpenAI"):
        await provider.generate("q", ProviderConfig())


async def test_anthropic_parses_response() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "content": [{"text": "claude"}],
                "usage": {"input_tokens": 4, "output_tokens": 2},
            },
        )

    provider = AnthropicProvider(api_key="test-key", transport=httpx.MockTransport(handler))
    result = await provider.generate("q", ProviderConfig(model="claude-3"))
    assert result.text == "claude"
    assert result.usage.prompt_tokens == 4
    assert result.usage.completion_tokens == 2


async def test_anthropic_missing_key_raises() -> None:
    provider = AnthropicProvider(api_key=None)
    with pytest.raises(ProviderError, match="Anthropic"):
        await provider.generate("q", ProviderConfig())


async def test_mistral_parses_response() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "m"}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1},
            },
        )

    provider = MistralProvider(api_key="test-key", transport=httpx.MockTransport(handler))
    result = await provider.generate("q", ProviderConfig(model="mistral-small"))
    assert result.text == "m"


async def test_mistral_missing_key_raises() -> None:
    provider = MistralProvider(api_key=None)
    with pytest.raises(ProviderError, match="Mistral"):
        await provider.generate("q", ProviderConfig())
