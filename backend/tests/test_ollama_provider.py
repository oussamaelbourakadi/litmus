"""OllamaProvider request construction and response parsing (mocked transport)."""

from __future__ import annotations

import json

import httpx

from app.providers.base import ProviderConfig
from app.providers.ollama import OllamaProvider


async def test_parses_response_and_usage() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"response": "pong", "prompt_eval_count": 3, "eval_count": 1},
        )

    provider = OllamaProvider(
        base_url="http://ollama:11434", transport=httpx.MockTransport(handler)
    )
    result = await provider.generate("ping", ProviderConfig(model="llama3", seed=7))
    assert result.text == "pong"
    assert result.usage.prompt_tokens == 3
    assert result.usage.completion_tokens == 1


async def test_sends_expected_payload() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(200, json={"response": "x"})

    provider = OllamaProvider(
        base_url="http://ollama:11434", transport=httpx.MockTransport(handler)
    )
    await provider.generate(
        "hi", ProviderConfig(model="llama3", temperature=0.2, max_tokens=64, seed=5)
    )
    assert captured["model"] == "llama3"
    assert captured["prompt"] == "hi"
    assert captured["stream"] is False
    options = captured["options"]
    assert isinstance(options, dict)
    assert options["seed"] == 5
    assert options["num_predict"] == 64
