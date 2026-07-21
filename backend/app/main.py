"""FastAPI application factory: middleware, lifespan, routers."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.catalog import router as catalog_router
from app.api.compare import router as compare_router
from app.api.datasets import router as datasets_router
from app.api.health import router as health_router
from app.api.projects import router as projects_router
from app.api.runs import router as runs_router
from app.config import get_settings
from app.db.session import AsyncSessionLocal
from app.engine.execution import CancellationRegistry

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("litmus")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: cancel in-flight runs and dispose the DB engine."""
    settings = get_settings()
    logger.info(
        "Starting %s v%s (%s)",
        settings.project_name,
        settings.version,
        settings.environment,
    )
    yield

    # Stop any in-flight background run tasks (not durable yet — see 1.8.2).
    tasks: list[asyncio.Task[None]] = list(app.state.run_tasks)
    for task in tasks:
        task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

    from app.db.session import engine

    await engine.dispose()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        summary="Ship AI you can trust — evaluate, red-team, and monitor AI systems.",
        lifespan=lifespan,
    )

    # Background-run execution state (see app/engine/execution.py).
    app.state.run_session_factory = AsyncSessionLocal
    app.state.cancellations = CancellationRegistry()
    app.state.run_tasks = set()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
        # Never leak stack traces to clients.
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    app.include_router(health_router)
    app.include_router(catalog_router)
    app.include_router(projects_router)
    app.include_router(datasets_router)
    app.include_router(runs_router)
    app.include_router(compare_router)
    return app


app = create_app()
