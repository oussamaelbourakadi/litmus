"""Anthropic provider (raw httpx). Optional — requires ANTHROPIC_API_KEY."""

from __future__ import annotations

from time import perf_counter

import httpx

from app.config import get_settings
from app.providers._http import PooledHttpClient
from app.providers.base import (
    GenerateResult,
    ModelProvider,
    ProviderConfig,
    ProviderError,
    Usage,
    provider_registry,
)


@provider_registry.register("anthropic")
class AnthropicProvider(ModelProvider):
    name = "anthropic"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.anthropic_api_key
        self._base_url = (base_url or settings.anthropic_base_url).rstrip("/")
        self._version = settings.anthropic_version
        self._http = PooledHttpClient(
            timeout=timeout or settings.request_timeout, transport=transport
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def generate(self, prompt: str, config: ProviderConfig) -> GenerateResult:
        if not self._api_key:
            raise ProviderError("Anthropic API key not configured (set ANTHROPIC_API_KEY)")

        payload = {
            "model": config.model,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        start = perf_counter()
        response = await self._http.get().post(
            f"{self._base_url}/messages",
            json=payload,
            headers={"x-api-key": self._api_key, "anthropic-version": self._version},
        )
        response.raise_for_status()
        data = response.json()
        latency_ms = (perf_counter() - start) * 1000

        text = data["content"][0]["text"]
        usage_data = data.get("usage", {})
        usage = Usage(
            prompt_tokens=int(usage_data.get("input_tokens", 0)),
            completion_tokens=int(usage_data.get("output_tokens", 0)),
        )
        return GenerateResult(text=text, usage=usage, latency_ms=latency_ms)
