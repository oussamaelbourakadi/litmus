"""LitmusClient tests with a mocked HTTP transport."""

from __future__ import annotations

import httpx

from litmus.client import LitmusClient


def test_health() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": "ok", "version": "0.1.0", "environment": "test"})

    with LitmusClient("http://litmus", transport=httpx.MockTransport(handler)) as client:
        assert client.health()["status"] == "ok"


def test_create_project_posts() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["url"] = str(request.url)
        return httpx.Response(201, json={"id": "1", "name": "P", "slug": "p"})

    with LitmusClient("http://litmus", transport=httpx.MockTransport(handler)) as client:
        project = client.create_project("P", "p")
    assert project["id"] == "1"
    assert seen["method"] == "POST"
