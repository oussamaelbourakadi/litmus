"""ProviderTarget — wrap a ModelProvider as an evaluable target."""

from __future__ import annotations

from app.providers.base import ModelProvider, ProviderConfig
from app.targets.base import Target, TargetResponse, target_registry


@target_registry.register("provider")
class ProviderTarget(Target):
    """Evaluate a model provider directly."""

    name = "provider"

    def __init__(self, provider: ModelProvider, config: ProviderConfig | None = None) -> None:
        self._provider = provider
        self._config = config or ProviderConfig()

    async def run(self, input: str) -> TargetResponse:
        result = await self._provider.generate(input, self._config)
        return TargetResponse(
            output=result.text,
            latency_ms=result.latency_ms,
            metadata={
                "model": self._config.model,
                "prompt_tokens": result.usage.prompt_tokens,
                "completion_tokens": result.usage.completion_tokens,
            },
        )

    async def aclose(self) -> None:
        await self._provider.aclose()
