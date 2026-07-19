"""Async engine and session factory.

``build_async_engine`` makes a managed-Postgres URL (Neon, Supabase, Render, …)
work with the asyncpg driver: it strips libpq-only query params that asyncpg
rejects (``sslmode``, ``channel_binding``) and translates an SSL requirement into
asyncpg connect args. Engine creation is lazy, so importing this module in tests
that target SQLite does not require a running PostgreSQL.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

_SSL_REQUIRING_MODES = {"require", "verify-ca", "verify-full"}


def _prepare_asyncpg_url(url: str) -> tuple[str, dict[str, Any]]:
    """Return an asyncpg-safe URL and connect args derived from libpq SSL params."""
    parts = urlsplit(url)
    # Fast path: no query means nothing to strip. Also avoids an urlunsplit
    # round-trip that would mangle authority-less URLs like sqlite:///path.
    if not parts.query:
        return url, {}
    connect_args: dict[str, Any] = {}
    kept: list[tuple[str, str]] = []
    for key, value in parse_qsl(parts.query):
        if key == "sslmode":
            if value in _SSL_REQUIRING_MODES:
                connect_args["ssl"] = True
            continue
        if key == "channel_binding":
            continue
        kept.append((key, value))
    cleaned = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(kept), parts.fragment))
    return cleaned, connect_args


def build_async_engine(url: str, **kwargs: Any) -> AsyncEngine:
    """Create an async engine, applying asyncpg SSL handling for managed Postgres."""
    cleaned, connect_args = _prepare_asyncpg_url(url)
    if connect_args:
        merged: dict[str, Any] = {**kwargs.get("connect_args", {}), **connect_args}
        kwargs["connect_args"] = merged
    return create_async_engine(cleaned, **kwargs)


_settings = get_settings()

engine = build_async_engine(_settings.database_url, echo=False, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields a request-scoped async session."""
    async with AsyncSessionLocal() as session:
        yield session
