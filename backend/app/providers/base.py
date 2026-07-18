"""Provider interface and registry (Phase 1.0 seed).

A provider turns a prompt into text plus usage/latency metadata. Every provider
is an async class implementing :meth:`ModelProvider.generate` and registered via
``@provider_registry.register("name")``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.core.registry import Registry


class ProviderError(RuntimeError):
    """Raised when a provider cannot fulfil a request (e.g. missing API key)."""


@dataclass(slots=True)
class ProviderConfig:
    """Generation parameters. ``seed`` enables reproducible runs."""

    model: str = "mock"
    temperature: float = 0.0
    max_tokens: int = 512
    seed: int | None = None
    extra: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class Usage:
    """Token accounting for a single generation."""

    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass(slots=True)
class GenerateResult:
    """Result of a single generation call."""

    text: str
    usage: Usage
    latency_ms: float


class ModelProvider(ABC):
    """Abstract, provider-agnostic text generator."""

    name: str = "base"

    @abstractmethod
    async def generate(self, prompt: str, config: ProviderConfig) -> GenerateResult:
        """Generate a completion for ``prompt`` under ``config``."""
        raise NotImplementedError


provider_registry: Registry[ModelProvider] = Registry("provider")
