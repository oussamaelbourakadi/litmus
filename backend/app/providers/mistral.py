"""Mistral provider (raw httpx). Optional — requires MISTRAL_API_KEY."""

from __future__ import annotations

from time import perf_counter

import httpx

from app.config import get_settings
from app.providers.base import (
    GenerateResult,
    ModelProvider,
    ProviderConfig,
    ProviderError,
    Usage,
    provider_registry,
)


@provider_registry.register("mistral")
class MistralProvider(ModelProvider):
    name = "mistral"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.mistral_api_key
        self._base_url = (base_url or settings.mistral_base_url).rstrip("/")
        self._timeout = timeout or settings.request_timeout
        self._transport = transport

    async def generate(self, prompt: str, config: ProviderConfig) -> GenerateResult:
        if not self._api_key:
            raise ProviderError("Mistral API key not configured (set MISTRAL_API_KEY)")

        payload = {
            "model": config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }

        start = perf_counter()
        async with httpx.AsyncClient(transport=self._transport, timeout=self._timeout) as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            response.raise_for_status()
            data = response.json()
        latency_ms = (perf_counter() - start) * 1000

        text = data["choices"][0]["message"]["content"]
        usage_data = data.get("usage", {})
        usage = Usage(
            prompt_tokens=int(usage_data.get("prompt_tokens", 0)),
            completion_tokens=int(usage_data.get("completion_tokens", 0)),
        )
        return GenerateResult(text=text, usage=usage, latency_ms=latency_ms)
