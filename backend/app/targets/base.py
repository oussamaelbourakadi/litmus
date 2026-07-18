"""Target interface and registry.

A Target is the system under evaluation. It turns an input string into an
output plus timing/metadata, hiding whether the system is a model provider or a
remote HTTP endpoint.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.core.registry import Registry


@dataclass(slots=True)
class TargetResponse:
    """A single response produced by a target."""

    output: str
    latency_ms: float
    metadata: dict[str, object] = field(default_factory=dict)


class Target(ABC):
    """Abstract system-under-test."""

    name: str = "base"

    @abstractmethod
    async def run(self, input: str) -> TargetResponse:
        """Run the target on ``input`` and return its response."""
        raise NotImplementedError


target_registry: Registry[Target] = Registry("target")
