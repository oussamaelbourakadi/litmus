"""A lazily-created, reusable httpx.AsyncClient for a provider instance."""

from __future__ import annotations

import httpx


class PooledHttpClient:
    """Owns one AsyncClient per provider, reused across calls and closed on aclose."""

    def __init__(self, *, timeout: float, transport: httpx.AsyncBaseTransport | None) -> None:
        self._timeout = timeout
        self._transport = transport
        self._client: httpx.AsyncClient | None = None

    def get(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                transport=self._transport,
                timeout=self._timeout,
                limits=httpx.Limits(max_connections=64, max_keepalive_connections=16),
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
