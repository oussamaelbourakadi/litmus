"""Catalog API: registered providers and targets are discoverable."""

from __future__ import annotations

from httpx import AsyncClient


async def test_list_providers(client: AsyncClient) -> None:
    response = await client.get("/providers")
    assert response.status_code == 200
    names = response.json()["providers"]
    for expected in ("mock", "ollama", "openai", "anthropic", "mistral"):
        assert expected in names


async def test_list_targets(client: AsyncClient) -> None:
    response = await client.get("/targets")
    assert response.status_code == 200
    names = response.json()["targets"]
    assert "provider" in names
    assert "http" in names
