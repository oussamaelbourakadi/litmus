"""Catalog endpoints: list registered providers and targets (read-only).

Execution endpoints arrive with the runner in Phase 1.3; here we only expose
what the plugin registries know about.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.providers import provider_registry
from app.targets import target_registry

router = APIRouter(tags=["catalog"])


@router.get("/providers", summary="List registered model providers")
async def list_providers() -> dict[str, list[str]]:
    return {"providers": provider_registry.names()}


@router.get("/targets", summary="List registered target types")
async def list_targets() -> dict[str, list[str]]:
    return {"targets": target_registry.names()}
