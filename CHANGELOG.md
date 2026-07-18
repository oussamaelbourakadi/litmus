# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added — Phase 1.4 (compare & regression)

- Engine `compare_runs`: aggregate deltas, per-case regression/improvement
  classification, and a configurable threshold verdict (absolute or relative) —
  the primitive behind the CI gate.
- API: `POST /compare`, list datasets per project, list runs per dataset, and
  append test cases to a dataset via JSON or CSV (text field, no new dependency).

### Added — Phase 1.3 (runner, metrics, persistence)

- Models `Dataset`, `TestCase`, `EvalRun`, `CaseResult` + Alembic migration 0002.
- Engine: `EvalRunner` (per-case error isolation, AND verdict, repeats),
  `metrics` (success rate, latency P50/P95, cost via price table, per-evaluator
  pass rates, mean±std over repeats), and seeded `bootstrap_ci`.
- API: create/list/get projects, create/get datasets with test cases, launch a
  run (synchronous) and read results + aggregates. Runs are persisted.
- Confidence intervals on the aggregate success rate (bootstrap, seeded).

### Added — Phase 1.2 (evaluators)

- Evaluators registered on `evaluator_registry`: `ExactMatch` (normalized),
  `RegexMatch`, `JsonSchema` (via `jsonschema`), and `LLMJudge` (rubric-based,
  JSON verdict with robust float fallback, provider-agnostic).
- Judge calibration utilities: `judge_agreement` (accuracy vs human labels) and
  `cohen_kappa`.
- `Evaluator.score` is now async and takes a typed `EvalCase`.
- `MockProvider` gained a `default` response for deterministic judge tests.
- Read-only `GET /evaluators` catalog endpoint.

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
