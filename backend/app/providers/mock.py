"""Deterministic mock provider — the backbone of reproducible tests and demos.

Requires no network and no API key. For a given ``(prompt, seed)`` it always
returns the same text, so evaluation runs are byte-for-byte reproducible.
"""

from __future__ import annotations

import hashlib

from app.providers.base import (
    GenerateResult,
    ModelProvider,
    ProviderConfig,
    Usage,
    provider_registry,
)


@provider_registry.register("mock")
class MockProvider(ModelProvider):
    """Provider that echoes a deterministic, seed-dependent response.

    Optionally, ``responses`` maps exact prompts to canned outputs, which is
    convenient for asserting evaluator behaviour in tests.
    """

    name = "mock"

    def __init__(self, responses: dict[str, str] | None = None) -> None:
        self._responses = responses or {}

    async def generate(self, prompt: str, config: ProviderConfig) -> GenerateResult:
        if prompt in self._responses:
            text = self._responses[prompt]
        else:
            text = self._synthesize(prompt, config.seed)
        usage = Usage(
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(text.split()),
        )
        return GenerateResult(text=text, usage=usage, latency_ms=0.0)

    @staticmethod
    def _synthesize(prompt: str, seed: int | None) -> str:
        digest = hashlib.sha256(f"{seed}:{prompt}".encode()).hexdigest()[:8]
        return f"mock[{digest}]: {prompt.strip()[:80]}"
