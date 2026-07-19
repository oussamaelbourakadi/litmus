<div align="center">

# Litmus

### Ship AI you can trust.

Open-source, self-hostable platform to **evaluate**, **red-team**, and **monitor** AI
systems — LLMs, RAG, agents, and vision — before and after production.
**Runs with no API key.**

[![CI](https://github.com/oussamaelbourakadi/litmus/actions/workflows/ci.yml/badge.svg)](https://github.com/oussamaelbourakadi/litmus/actions/workflows/ci.yml)
[![Litmus Eval Gate](https://github.com/oussamaelbourakadi/litmus/actions/workflows/litmus-eval.yml/badge.svg)](https://github.com/oussamaelbourakadi/litmus/actions/workflows/litmus-eval.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)
![Node 24](https://img.shields.io/badge/node-24-green.svg)

**Try it in 5 minutes locally** with `docker compose up` — no API key. See the
[Portfolio Demo](#portfolio-demo) below.

</div>

---

> **Status:** Phase 1 — **Evaluate** — is complete: engine, metrics with confidence
> intervals, run comparison / regression gate, dashboard, and an SDK + CLI + GitHub
> Action. Red-Team (OWASP LLM), adversarial Vision, and Monitor are on the roadmap.

## Portfolio Demo

Litmus is a portfolio / CV project. It does **not** require any hosted service —
the intended way to see it is the **local Docker demo** (no API key, no account):

```bash
git clone https://github.com/oussamaelbourakadi/litmus.git
cd litmus
docker compose up --build
# Dashboard → http://localhost:3000   ·   API docs → http://localhost:8000/docs
```

Then: create a project → add a dataset (CSV) → launch a run → open the run detail
→ launch a second run → compare them and watch the regression get highlighted.

<table>
  <tr>
    <td width="50%"><img src="docs/media/dashboard.png" alt="Dashboard" /></td>
    <td width="50%"><img src="docs/media/runs.png" alt="Run detail" /></td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/media/compare.png" alt="Run comparison" /></td>
    <td width="50%"><img src="docs/media/metrics.png" alt="Metrics with confidence intervals" /></td>
  </tr>
</table>

> The images above are labeled **placeholders**. Replace them with real
> screenshots of your running instance — see
> [`docs/media/README.md`](./docs/media/README.md) for exactly what to capture.

### Record a 2-minute demo video

A short screen recording makes the project instantly legible to a recruiter:

1. Start the stack: `docker compose up --build` and open `http://localhost:3000`.
2. Record your screen (free tools): **Windows** Xbox Game Bar (`Win+G`) or
   [OBS Studio](https://obsproject.com/); **macOS** `Cmd+Shift+5`; **Linux** OBS.
3. Follow this ~2-minute script:
   - **0:00** — Landing page → "Open the dashboard".
   - **0:15** — Create a project, then a dataset; upload a small CSV of test cases.
   - **0:40** — Launch a run (mock provider, exact-match evaluator).
   - **1:00** — Open the run detail: point out the **success rate with its bootstrap
     confidence interval**, latency P50/P95, and the per-case results table.
   - **1:30** — Launch a second, weaker run; **Compare** the two → show the
     highlighted regressions and the **verdict** badge.
   - **1:50** — Mention it runs with **no API key** and the CLI gates CI on regression.
4. Export as MP4, upload it (GitHub release asset, YouTube unlisted, or Loom), and
   link it here.

## Why Litmus

Litmus is a **professional-grade demonstrator** that coexists with tools like
Promptfoo, DeepEval, and Langfuse — not a clone. Its differentiation:

- **Statistical rigor** — bootstrap confidence intervals on every aggregate, fixed seeds, reproducible runs. No invented metrics.
- **Runs with no API key** — mock + local (Ollama) providers, so anyone can clone and try it.
- **A real CI gate** — an SDK + CLI + GitHub Action that fails the build on regression.
- **Clean plugin architecture** — a provider, evaluator, target (and later attack) is a single class + a decorator. Adding a capability never touches the core.
- **Adversarial vision / multimodal module** (roadmap) — largely absent from text-only competitors.

## Three pillars, aligned with the lifecycle

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    EVALUATE     │    │    RED-TEAM     │    │    MONITOR      │
│ (before deploy) │    │ (before deploy) │    │ (after deploy)  │
│                 │    │                 │    │                 │
│ Metrics + CI    │    │ OWASP LLM Top10 │    │ Live traces     │
│ Comparison      │    │ Adversarial     │    │ Drift + alerts  │
│ Regression gate │    │ vision attacks  │    │ Trace-to-test   │
│   ✅ shipped    │    │   ⏳ roadmap    │    │   ⏳ roadmap    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Architecture

```mermaid
flowchart LR
    subgraph Clients
      UI[Next.js dashboard]
      CLI[Python SDK / CLI]
      GHA[GitHub Action gate]
    end
    subgraph Backend[FastAPI backend]
      API[API routers]
      ENG[Engine<br/>runner · metrics · compare]
      REG[(Plugin registry)]
      PROV[Providers<br/>mock · ollama · openai · …]
      EVAL[Evaluators<br/>exact · regex · json · llm-judge]
      TGT[Targets<br/>provider · http]
    end
    DB[(PostgreSQL)]

    UI --> API
    CLI --> API
    GHA --> CLI
    API --> ENG
    ENG --> REG
    REG --- PROV
    REG --- EVAL
    REG --- TGT
    ENG --> DB
```

## Evaluate — what ships today

- **Providers:** Mock (deterministic, seeded), Ollama (local, no key), OpenAI / Anthropic / Mistral (optional, env-gated).
- **Evaluators:** ExactMatch, RegexMatch, JsonSchema, LLMJudge (rubric → JSON verdict) + judge calibration (agreement, Cohen's kappa).
- **Engine:** per-case error isolation, AND verdict, repeats; metrics = success rate **with bootstrap CI**, latency P50/P95, cost (price table), per-evaluator pass rates.
- **Compare:** aggregate deltas + per-case regressions + an absolute/relative **threshold verdict**.
- **Dashboard:** projects → datasets (CSV upload) → runs → metric cards + per-case table → comparison with highlighted regressions.
- **SDK + CLI + GitHub Action:** local, serverless runs that **fail CI on regression**.

## Quickstart (5 minutes, no API key)

```bash
git clone https://github.com/oussamaelbourakadi/litmus.git
cd litmus
docker compose up --build
```

- API: http://localhost:8000 (Swagger `/docs`, health `/health`)
- Dashboard: http://localhost:3000

## CLI / SDK / GitHub Action

**CLI** (serverless, exits non-zero on regression):

```bash
uv pip install ./sdk
litmus init                       # scaffold litmus.yaml + a demo target
litmus run --config litmus.yaml   # evaluate and gate on regressions
```

**SDK** (run an eval in ~10 lines):

```python
from litmus import Case, ExactMatch, run_local

cases = [Case(input="capital of France?", expected="Paris")]
result = run_local(cases, lambda prompt: "Paris", [ExactMatch()])
print(result.success_rate, result.ci_low, result.ci_high)
```

**GitHub Action** — add the [`litmus-eval.yml`](./.github/workflows/litmus-eval.yml)
workflow; it installs the SDK and fails the build when the success rate drops
below your baseline.

## Extending Litmus (plugin architecture)

Adding a capability is always the same shape — write a class, register it:

```python
from app.providers import ModelProvider, provider_registry

@provider_registry.register("my-provider")
class MyProvider(ModelProvider):
    name = "my-provider"
    async def generate(self, prompt, config):
        ...
```

The same pattern applies to evaluators (`evaluator_registry`) and targets
(`target_registry`). The engine discovers plugins by name; the core never changes.

## Repository structure

```
litmus/
├── backend/     FastAPI · SQLAlchemy 2 async · Alembic · engine · plugin registry
├── frontend/    Next.js (App Router) · TypeScript strict · Tailwind dashboard
├── sdk/         litmus-sdk — local runner + Typer CLI + CI gate
├── examples/    demo target, dataset, litmus.yaml, SDK quickstart
├── docs/        DEPLOY.md · PORTFOLIO_BLURB.md
├── docker-compose.yml
└── .github/workflows/   ci.yml · litmus-eval.yml
```

## Roadmap

| Phase | Pillar | Status |
|-------|--------|--------|
| 1 | **Evaluate** — engine, metrics, comparison, dashboard, SDK/CLI, CI gate | ✅ shipped |
| 2 | **Red-Team (LLM)** — OWASP LLM Top 10 attacks, defenses, report | ⏳ planned |
| 3 | **Adversarial Vision** — FGSM/PGD/patch, face-recognition showcase | ⏳ planned |
| 4 | **Monitor** — traces, online eval, drift, alerts, trace-to-test | ⏳ planned |
| 5 | **Product** — auth, multi-project, docs, landing | ⏳ planned |

Contributions welcome — see the issue templates and PR checklist.

## Deployment (optional)

A permanent hosted demo is **not required** — the primary demo is local Docker
(above). If you do want one, there's a fully **card-free** path: backend on
**Hugging Face Spaces** (Docker), database on **Neon** (serverless Postgres),
frontend on **Vercel** — see [`docs/DEPLOY.md`](./docs/DEPLOY.md).

## Author

**Oussama El Bourakadi** — [github.com/oussamaelbourakadi](https://github.com/oussamaelbourakadi)

## License

[MIT](./LICENSE)
