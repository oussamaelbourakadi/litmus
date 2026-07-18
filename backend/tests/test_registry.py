"""Plugin registry tests — the backbone of the plugin architecture."""

from __future__ import annotations

import pytest

from app.core.registry import Registry


def test_register_and_get_is_case_insensitive() -> None:
    registry: Registry[object] = Registry("widget")

    @registry.register("Alpha")
    class Alpha:
        pass

    assert "alpha" in registry
    assert "ALPHA" in registry
    assert registry.get("alpha") is Alpha
    assert registry.get("ALPHA") is Alpha
    assert registry.names() == ["alpha"]
    assert len(registry) == 1


def test_duplicate_registration_raises() -> None:
    registry: Registry[object] = Registry("widget")

    @registry.register("dup")
    class First:
        pass

    with pytest.raises(ValueError, match="already registered"):

        @registry.register("DUP")
        class Second:
            pass


def test_unknown_lookup_raises() -> None:
    registry: Registry[object] = Registry("widget")
    with pytest.raises(KeyError, match="unknown widget"):
        registry.get("missing")


def test_builtin_registries_are_wired() -> None:
    from app.evaluators import evaluator_registry
    from app.providers import provider_registry

    # Providers (1.1) and evaluators (1.2) are registered on import.
    assert "mock" in provider_registry
    assert "ollama" in provider_registry
    assert "exact_match" in evaluator_registry
    assert "llm_judge" in evaluator_registry
