"""ProviderTarget behaviour and target registry population."""

from __future__ import annotations

from app.providers.base import ProviderConfig
from app.providers.mock import MockProvider
from app.targets import target_registry
from app.targets.provider_target import ProviderTarget


async def test_provider_target_returns_output() -> None:
    target = ProviderTarget(
        MockProvider(responses={"q": "a"}),
        ProviderConfig(model="mock"),
    )
    response = await target.run("q")
    assert response.output == "a"
    assert response.metadata["model"] == "mock"


def test_target_registry_is_populated() -> None:
    assert "provider" in target_registry
    assert "http" in target_registry
