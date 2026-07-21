"""Retry with exponential backoff + full jitter for transient failures.

Transient = network/transport errors and HTTP 429/5xx. Non-transient errors
(missing API key, 4xx, bugs) are raised immediately. The ``sleep`` callable is
injectable so tests run with zero delay.
"""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

import httpx

_TRANSIENT_STATUS = frozenset({429, 500, 502, 503, 504})


@dataclass(slots=True)
class RetryPolicy:
    max_attempts: int = 4
    base_delay: float = 0.5
    max_delay: float = 8.0
    jitter: bool = True


def is_transient(exc: BaseException) -> bool:
    """Whether a failure is worth retrying (network/transport or HTTP 429/5xx)."""
    if isinstance(exc, httpx.TransportError):  # includes TimeoutException
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in _TRANSIENT_STATUS
    return False


async def with_retries[T](
    func: Callable[[], Awaitable[T]],
    policy: RetryPolicy,
    *,
    transient: Callable[[BaseException], bool] = is_transient,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> T:
    """Call ``func`` with retries; re-raise the last error when attempts run out."""
    attempt = 0
    while True:
        try:
            return await func()
        except Exception as exc:
            attempt += 1
            if attempt >= policy.max_attempts or not transient(exc):
                raise
            delay = min(policy.max_delay, policy.base_delay * (2 ** (attempt - 1)))
            if policy.jitter:
                delay = random.uniform(0.0, delay)  # full jitter
            await sleep(delay)
