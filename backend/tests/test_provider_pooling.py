"""Provider HTTP-client pooling and aclose."""

from __future__ import annotations

import httpx

from app.providers.base import ProviderConfig
from app.providers.ollama import OllamaProvider


def _ok(_: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"response": "ok"})


async def test_client_is_reused_across_calls() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, json={"response": "ok"})

    provider = OllamaProvider(base_url="http://x", transport=httpx.MockTransport(handler))
    first = provider._http.get()
    await provider.generate("a", ProviderConfig(model="m"))
    await provider.generate("b", ProviderConfig(model="m"))
    second = provider._http.get()

    assert first is second
    assert calls["n"] == 2
    await provider.aclose()


async def test_aclose_closes_the_client() -> None:
    provider = OllamaProvider(base_url="http://x", transport=httpx.MockTransport(_ok))
    client = provider._http.get()
    assert client.is_closed is False
    await provider.aclose()
    assert client.is_closed is True
