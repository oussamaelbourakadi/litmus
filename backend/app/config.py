"""Application settings loaded from the environment (never hard-coded secrets)."""

from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings.

    Every value has a safe default so the platform boots with **no API key**.
    Values are overridable through environment variables or a local ``.env``.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    project_name: str = "Litmus"
    version: str = "0.1.0"
    environment: str = "development"

    # postgresql+asyncpg driver for the async engine; localhost default for bare-metal dev.
    database_url: str = "postgresql+asyncpg://litmus:litmus@localhost:5432/litmus"
    redis_url: str = "redis://localhost:6379/0"

    cors_origins: list[str] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        """Allow a comma-separated string (env-friendly) as well as a JSON list."""
        if isinstance(value, str) and not value.strip().startswith("["):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings singleton."""
    return Settings()
