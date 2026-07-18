"""Shared test fixtures.

Tests never touch the network or require an API key. Database tests run against
an in-memory SQLite database created from the ORM metadata.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models  # noqa: F401  (register tables on Base.metadata)
from app.db.base import Base


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """HTTP client wired directly to the ASGI app (no live server)."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """Async session backed by a fresh in-memory SQLite schema."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()
