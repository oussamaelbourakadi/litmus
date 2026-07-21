"""Retry policy tests (zero-delay via an injected sleep)."""

from __future__ import annotations

import httpx
import pytest

from app.engine.retry import RetryPolicy, is_transient, with_retries


async def _no_sleep(_: float) -> None:
    return None


async def test_succeeds_after_transient_failures() -> None:
    calls = {"n": 0}

    async def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise httpx.ConnectError("boom")
        return "ok"

    result = await with_retries(flaky, RetryPolicy(max_attempts=5), sleep=_no_sleep)
    assert result == "ok"
    assert calls["n"] == 3


async def test_gives_up_after_max_attempts() -> None:
    calls = {"n": 0}

    async def always_fail() -> str:
        calls["n"] += 1
        raise httpx.ConnectError("boom")

    with pytest.raises(httpx.ConnectError):
        await with_retries(always_fail, RetryPolicy(max_attempts=3), sleep=_no_sleep)
    assert calls["n"] == 3


async def test_non_transient_is_not_retried() -> None:
    calls = {"n": 0}

    async def bad() -> str:
        calls["n"] += 1
        raise ValueError("nope")

    with pytest.raises(ValueError, match="nope"):
        await with_retries(bad, RetryPolicy(max_attempts=5), sleep=_no_sleep)
    assert calls["n"] == 1


def test_is_transient_classification() -> None:
    request = httpx.Request("GET", "http://x")
    assert is_transient(httpx.ConnectTimeout("x")) is True
    assert is_transient(httpx.ConnectError("x")) is True
    resp429 = httpx.Response(429, request=request)
    assert is_transient(httpx.HTTPStatusError("x", request=request, response=resp429)) is True
    resp404 = httpx.Response(404, request=request)
    assert is_transient(httpx.HTTPStatusError("x", request=request, response=resp404)) is False
    assert is_transient(ValueError("x")) is False
