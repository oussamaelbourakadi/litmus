"""Helpers for instantiating providers by name from the registry.

Importing this module also imports the ``app.providers`` package, which registers
every concrete provider — so ``make_provider`` always sees them.
"""

from __future__ import annotations

from app.providers.base import ModelProvider, provider_registry


def make_provider(name: str) -> ModelProvider:
    """Instantiate a registered provider by name (raises KeyError if unknown)."""
    return provider_registry.get(name)()
