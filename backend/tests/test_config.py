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


def test_database_url_postgres_scheme_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@host:5432/db")
    settings = Settings()
    assert settings.database_url == "postgresql+asyncpg://u:p@host:5432/db"


def test_database_url_postgresql_scheme_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@host/db")
    settings = Settings()
    assert settings.database_url == "postgresql+asyncpg://u:p@host/db"


def test_database_url_async_scheme_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@host/db")
    settings = Settings()
    assert settings.database_url == "postgresql+asyncpg://u:p@host/db"


def test_neon_sslmode_is_stripped_and_ssl_enabled() -> None:
    from app.db.session import _prepare_asyncpg_url

    cleaned, connect_args = _prepare_asyncpg_url(
        "postgresql+asyncpg://u:p@ep.neon.tech/db?sslmode=require"
    )
    assert "sslmode" not in cleaned
    assert connect_args == {"ssl": True}


def test_channel_binding_is_stripped() -> None:
    from app.db.session import _prepare_asyncpg_url

    cleaned, connect_args = _prepare_asyncpg_url(
        "postgresql+asyncpg://u:p@h/db?sslmode=require&channel_binding=require"
    )
    assert "channel_binding" not in cleaned
    assert "sslmode" not in cleaned
    assert connect_args == {"ssl": True}


def test_plain_url_is_unchanged() -> None:
    from app.db.session import _prepare_asyncpg_url

    url = "postgresql+asyncpg://litmus:litmus@postgres:5432/litmus"
    cleaned, connect_args = _prepare_asyncpg_url(url)
    assert cleaned == url
    assert connect_args == {}
