"""Ollama provider — local models, no API key.

Talks to a running Ollama server via its HTTP API. An optional ``transport``
lets tests inject a mocked HTTP layer with no real network.
"""

from __future__ import annotations

from time import perf_counter

import httpx

from app.config import get_settings
from app.providers.base import (
    GenerateResult,
    ModelProvider,
    ProviderConfig,
    Usage,
    provider_registry,
)


@provider_registry.register("ollama")
class OllamaProvider(ModelProvider):
    name = "ollama"

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        settings = get_settings()
        self._base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self._timeout = timeout or settings.request_timeout
        self._transport = transport

    async def generate(self, prompt: str, config: ProviderConfig) -> GenerateResult:
        payload = {
            "model": config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
                "seed": config.seed,
            },
        }
        start = perf_counter()
        async with httpx.AsyncClient(transport=self._transport, timeout=self._timeout) as client:
            response = await client.post(f"{self._base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
        latency_ms = (perf_counter() - start) * 1000

        usage = Usage(
            prompt_tokens=int(data.get("prompt_eval_count", 0)),
            completion_tokens=int(data.get("eval_count", 0)),
        )
        return GenerateResult(text=data.get("response", ""), usage=usage, latency_ms=latency_ms)
