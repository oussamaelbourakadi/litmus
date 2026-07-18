"""Targets — the systems under evaluation.

Importing this package registers every concrete target on ``target_registry``.
"""

from __future__ import annotations

from app.targets.base import Target, TargetResponse, target_registry
from app.targets.http_target import HttpTarget, HttpTargetError
from app.targets.provider_target import ProviderTarget

__all__ = [
    "HttpTarget",
    "HttpTargetError",
    "ProviderTarget",
    "Target",
    "TargetResponse",
    "target_registry",
]
