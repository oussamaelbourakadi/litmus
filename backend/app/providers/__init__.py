"""Model providers.

Concrete providers (Mock, Ollama, OpenAI, Anthropic, Mistral) land in Phase 1.1.
This package already exposes the :class:`ModelProvider` interface and the shared
``provider_registry`` so those implementations plug in without touching the engine.
"""

from __future__ import annotations

from app.providers.base import (
    GenerateResult,
    ModelProvider,
    ProviderConfig,
    Usage,
    provider_registry,
)

__all__ = [
    "GenerateResult",
    "ModelProvider",
    "ProviderConfig",
    "Usage",
    "provider_registry",
]
