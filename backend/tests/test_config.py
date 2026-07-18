"""Settings parsing tests — regression guard for env-provided CORS origins."""

from __future__ import annotations

import pytest

from app.config import Settings


def test_cors_origins_parses_comma_separated_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://a.example, http://b.example")
    settings = Settings()
    assert settings.cors_origins == ["http://a.example", "http://b.example"]


def test_cors_origins_single_value_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")
    settings = Settings()
    assert settings.cors_origins == ["http://localhost:3000"]


def test_cors_origins_defaults_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    settings = Settings()
    assert settings.cors_origins == ["http://localhost:3000"]
