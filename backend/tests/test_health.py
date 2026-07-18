"""Health / version endpoint tests."""

from __future__ import annotations

from httpx import AsyncClient


async def test_health_ok(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"]
    assert body["environment"]


async def test_version(client: AsyncClient) -> None:
    response = await client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Litmus"
    assert body["version"]
