"""Application settings loaded from the environment (never hard-coded secrets)."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


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

    # NoDecode disables pydantic-settings' JSON pre-parsing of this complex field
    # so a plain comma-separated env string (e.g. "a,b") is handled by the validator.
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        """Parse a comma-separated string from the environment into a list."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("database_url", mode="after")
    @classmethod
    def _normalize_db_url(cls, value: str) -> str:
        """Coerce Heroku/Render-style Postgres URLs to the async (asyncpg) driver."""
        if value.startswith("postgres://"):
            return "postgresql+asyncpg://" + value.removeprefix("postgres://")
        if value.startswith("postgresql://"):
            return "postgresql+asyncpg://" + value.removeprefix("postgresql://")
        return value

    # --- Providers ---------------------------------------------------------
    # Shared HTTP timeout (seconds) for provider/target requests.
    request_timeout: float = 30.0

    # Ollama (local, no key). Use host.docker.internal to reach a host Ollama from a container.
    ollama_base_url: str = "http://localhost:11434"

    # Optional cloud provider keys. Absent by default → the platform runs on
    # mock/local only; cloud providers raise a clear error if used without a key.
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    mistral_api_key: str | None = None

    openai_base_url: str = "https://api.openai.com/v1"
    anthropic_base_url: str = "https://api.anthropic.com/v1"
    mistral_base_url: str = "https://api.mistral.ai/v1"
    anthropic_version: str = "2023-06-01"

    # --- Execution (concurrency + resilience) ---
    run_concurrency: int = 8
    case_timeout: float = 60.0
    retry_max_attempts: int = 4
    retry_base_delay: float = 0.5
    retry_max_delay: float = 8.0

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings singleton."""
    return Settings()
