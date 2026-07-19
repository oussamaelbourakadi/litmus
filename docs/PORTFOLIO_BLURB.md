# Portfolio blurb — Litmus

## CV bullet (one line)

> **Litmus** — Built an open-source, self-hostable platform to evaluate, red-team, and monitor AI systems (FastAPI · SQLAlchemy async · Next.js · Python SDK): reproducible metrics with **bootstrap confidence intervals**, a plugin architecture for providers/evaluators, and a **regression CI gate** (SDK + CLI + GitHub Action) — runs with **no API key**.

## Paragraph (reusable summary)

Litmus is a professional-grade evaluation platform for AI systems. Phase 1 (Evaluate)
ships an async FastAPI backend with a clean plugin architecture (providers,
evaluators, targets discovered through a registry), a reproducible evaluation
engine with seeded **bootstrap confidence intervals** on every aggregate, run
comparison with regression detection and a configurable threshold verdict, a
Next.js dashboard, and a lightweight Python **SDK + CLI + GitHub Action** that
fails CI when quality regresses. Everything runs locally with **no API key**
(mock and Ollama providers), is fully typed (`mypy --strict`, `tsc --strict`),
and is covered by a blocking CI pipeline (lint, types, tests, Docker builds,
secret scan). The roadmap adds LLM red-teaming (OWASP LLM Top 10), an adversarial
**vision** module (FGSM/PGD/patch — the differentiator), and production monitoring.

## Six interview talking points

1. **Bootstrap confidence intervals.** Every aggregate (e.g. success rate) reports
   a seeded percentile-bootstrap interval, so results are reproducible and
   uncertainty is explicit — no invented point metrics.
2. **LLM-judge calibration.** The `LLMJudge` evaluator is provider-agnostic and
   returns a JSON verdict with a robust float fallback; `judge_agreement` and
   Cohen's kappa measure agreement against human labels, making "the judge is
   trustworthy" a measured claim rather than an assumption.
3. **Regression detection + threshold verdict.** `compare_runs` classifies
   per-case regressions/improvements and renders an absolute/relative threshold
   verdict — the exact primitive the SDK/CLI/GitHub Action use to gate CI.
4. **Plugin architecture.** Providers, evaluators, and targets are single classes
   registered via a generic `Registry`; adding a capability is a class plus a
   decorator, never a change to the engine.
5. **Per-case error isolation.** The runner isolates failures per case (a broken
   target or evaluator never sinks the whole run), and repeats yield mean±std —
   important for realistic, partially-failing evaluation suites.
6. **CI gate as a real developer tool.** A dependency-light SDK (no FastAPI/ORM)
   plus a Typer CLI (`litmus run`) exits non-zero on regression against a
   committed baseline; a GitHub Action wires this into any repo with no API key.

## Links

- Repository: https://github.com/oussamaelbourakadi/litmus
- Demo: run locally with `docker compose up` (no API key) — see the README's
  **Portfolio Demo** section and `docs/media/`. Optional hosted deploy in
  `docs/DEPLOY.md`.
