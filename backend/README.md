# Litmus — Backend

FastAPI (async) + SQLAlchemy 2 (async, asyncpg) + Alembic. Part of the
[Litmus](../README.md) monorepo.

## Local development

```bash
uv sync                       # install deps into .venv
uv run alembic upgrade head   # apply migrations (needs a running Postgres)
uv run uvicorn app.main:app --reload
```

## Quality gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

Tests use an in-memory SQLite database and require **no network and no API key**.
