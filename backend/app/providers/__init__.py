"""Model providers.

Importing this package registers every concrete provider on
``provider_registry`` (Mock and Ollama run with no API key; the cloud providers
are optional and gated by their env keys).
"""

from __future__ import annotations

# Import concrete providers for their registration side effects.
from app.providers.anthropic import AnthropicProvider
from app.providers.base import (
    GenerateResult,
    ModelProvider,
    ProviderConfig,
    ProviderError,
    Usage,
    provider_registry,
)
from app.providers.mistral import MistralProvider
from app.providers.mock import MockProvider
from app.providers.ollama import OllamaProvider
from app.providers.openai import OpenAIProvider
from app.providers.scripted import ScriptedProvider

__all__ = [
    "AnthropicProvider",
    "GenerateResult",
    "MistralProvider",
    "MockProvider",
    "ModelProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "ProviderConfig",
    "ProviderError",
    "ScriptedProvider",
    "Usage",
    "provider_registry",
]
