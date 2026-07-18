"""System endpoints: liveness and version."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.version,
        environment=settings.environment,
    )


@router.get("/version", summary="Product version")
async def version() -> dict[str, str]:
    settings = get_settings()
    return {"name": settings.project_name, "version": settings.version}
