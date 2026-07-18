"""Shared test fixtures.

Tests never touch the network or require an API key. Database tests run against
an in-memory SQLite database created from the ORM metadata.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

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


@pytest_asyncio.fixture
async def api_client() -> AsyncIterator[AsyncClient]:
    """ASGI client whose get_db dependency is backed by a shared in-memory SQLite.

    StaticPool keeps a single connection so every request in a test sees the same
    schema and data.
    """
    from app.db.session import get_db
    from app.main import app

    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client
    app.dependency_overrides.clear()
    await engine.dispose()
