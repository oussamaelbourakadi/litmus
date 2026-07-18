"""HttpTarget with a mocked HTTP transport (no real network)."""

from __future__ import annotations

import json
from collections.abc import Callable

import httpx
import pytest

from app.targets.http_target import HttpTarget, HttpTargetError


def _json_handler(
    payload: dict[str, object], status: int = 200
) -> Callable[[httpx.Request], httpx.Response]:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=payload)

    return handler


async def test_extracts_top_level_output() -> None:
    target = HttpTarget(
        "http://svc/api", transport=httpx.MockTransport(_json_handler({"output": "hi"}))
    )
    response = await target.run("prompt")
    assert response.output == "hi"
    assert response.metadata["status_code"] == 200


async def test_extracts_nested_output() -> None:
    transport = httpx.MockTransport(_json_handler({"data": {"text": "deep"}}))
    target = HttpTarget("http://svc/api", output_path=("data", "text"), transport=transport)
    response = await target.run("p")
    assert response.output == "deep"


async def test_missing_output_path_raises() -> None:
    transport = httpx.MockTransport(_json_handler({"wrong": "x"}))
    target = HttpTarget("http://svc/api", transport=transport)
    with pytest.raises(HttpTargetError):
        await target.run("p")


async def test_http_error_propagates() -> None:
    transport = httpx.MockTransport(_json_handler({}, status=500))
    target = HttpTarget("http://svc/api", transport=transport)
    with pytest.raises(httpx.HTTPStatusError):
        await target.run("p")


async def test_sends_configured_input_field() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(200, json={"output": "ok"})

    target = HttpTarget(
        "http://svc/api", input_field="query", transport=httpx.MockTransport(handler)
    )
    await target.run("hello")
    assert captured == {"query": "hello"}
