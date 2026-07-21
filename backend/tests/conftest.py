"""Shared test fixtures.

Tests never touch the network or require an API key. Database tests run against a
SQLite database created from the ORM metadata. The API fixture uses a file-based
SQLite so background run tasks can open their own sessions (as they do in prod).
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from pathlib import Path
from typing import Any

import pytest
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


@pytest_asyncio.fixture
async def api_client(tmp_path: Path) -> AsyncIterator[AsyncClient]:
    """ASGI client backed by a file-based SQLite shared with background run tasks."""
    from app.db.session import get_db
    from app.engine.execution import CancellationRegistry
    from app.main import app

    db_path = tmp_path / "test.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        connect_args={"check_same_thread": False, "timeout": 30},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.state.run_session_factory = session_factory
    app.state.cancellations = CancellationRegistry()
    app.state.run_tasks = set()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client

    # Stop any in-flight background run tasks before disposing the engine.
    for task in list(app.state.run_tasks):
        task.cancel()
    if app.state.run_tasks:
        await asyncio.gather(*app.state.run_tasks, return_exceptions=True)
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.fixture
def wait_for_run() -> Callable[[AsyncClient, str], Awaitable[dict[str, Any]]]:
    """Poll GET /runs/{id} until the run reaches a terminal state; return its body."""

    async def _wait(client: AsyncClient, run_id: str, max_wait: float = 5.0) -> dict[str, Any]:
        deadline = time.monotonic() + max_wait
        last = "unknown"
        while time.monotonic() < deadline:
            body = (await client.get(f"/runs/{run_id}")).json()
            last = body["status"]
            if last in {"completed", "failed", "cancelled"}:
                return body
            await asyncio.sleep(0.02)
        raise AssertionError(f"run {run_id} did not finish (last status={last})")

    return _wait
