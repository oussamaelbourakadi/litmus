"""Generic plugin registry.

The plugin architecture is a first-class citizen from day one: providers,
evaluators, attacks, defenses and connectors are all discovered through a
:class:`Registry`. Adding a capability = writing a class + ``@registry.register(...)``
decorator, never editing the engine.
"""

from __future__ import annotations

from collections.abc import Callable


class Registry[T]:
    """Name-indexed registry of plugin classes.

    Lookups are case-insensitive. Registering a duplicate name or fetching an
    unknown name fails loudly rather than silently returning the wrong plugin.
    """

    def __init__(self, kind: str) -> None:
        self._kind = kind
        self._items: dict[str, type[T]] = {}

    def register(self, name: str) -> Callable[[type[T]], type[T]]:
        """Decorator that registers a plugin class under ``name``."""
        key = name.lower()

        def decorator(cls: type[T]) -> type[T]:
            if key in self._items:
                raise ValueError(f"{self._kind} '{name}' is already registered")
            self._items[key] = cls
            return cls

        return decorator

    def get(self, name: str) -> type[T]:
        """Return the plugin class registered under ``name``."""
        try:
            return self._items[name.lower()]
        except KeyError:
            raise KeyError(f"unknown {self._kind}: '{name}'. available: {self.names()}") from None

    def names(self) -> list[str]:
        """Return the sorted list of registered names."""
        return sorted(self._items)

    def __contains__(self, name: str) -> bool:
        return name.lower() in self._items

    def __len__(self) -> int:
        return len(self._items)
