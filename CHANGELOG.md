# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added — Phase 1.1 (providers & targets)

- Concrete providers registered on `provider_registry`: `MockProvider`
  (deterministic, seeded), `OllamaProvider` (local, no key), and `OpenAIProvider`
  / `AnthropicProvider` / `MistralProvider` (raw httpx, gated by env keys).
- `Target` abstraction with `ProviderTarget` and `HttpTarget` (configurable JSON
  output path), both registered on `target_registry`.
- Read-only catalog endpoints `GET /providers` and `GET /targets`.
- Optional `OLLAMA_BASE_URL` in docker-compose; `httpx` promoted to a runtime
  dependency.

## [0.1.0] — 2026-07-18

### Added — Phase 1.0 (foundation)

- Monorepo scaffold: `backend/`, `frontend/`, docker-compose, CI, tooling.
- FastAPI (async) backend with `/health` and `/version`, CORS, safe error handling.
- Database layer: SQLAlchemy 2 (async, asyncpg), UUID/timestamp/soft-delete mixins,
  `Project` model, and Alembic (async) with the initial migration.
- Plugin architecture from day one: generic `Registry` plus `ModelProvider` and
  `Evaluator` interfaces with their registries.
- Next.js (App Router, TypeScript strict) + Tailwind dashboard shell.
- CI (GitHub Actions): ruff, mypy, pytest, ESLint, tsc, vitest, Next build,
  docker image builds, and gitleaks secret scan.
- MIT license, `.env.example` files (runs with **no API key**), Makefile.
