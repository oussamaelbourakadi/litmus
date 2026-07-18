"""Run endpoints: launch an evaluation run (synchronous) and read results.

Runs execute in-request for now; Celery/Redis will offload long runs (Ollama /
cloud) in a later sub-phase.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.engine.metrics import RunMetrics
from app.engine.runner import EvalRunner
from app.evaluators.base import EvalCase, Evaluator
from app.evaluators.exact_match import ExactMatch
from app.evaluators.json_schema import JsonSchema
from app.evaluators.llm_judge import LLMJudge
from app.evaluators.regex_match import RegexMatch
from app.models.case_result import CaseResult
from app.models.dataset import Dataset
from app.models.eval_run import EvalRun, RunStatus
from app.models.test_case import TestCase
from app.providers.base import ProviderConfig
from app.providers.registry_utils import make_provider
from app.schemas.run import (
    CaseResultRead,
    EvaluatorSpec,
    RunCreate,
    RunRead,
    RunSummaryRead,
)
from app.targets.provider_target import ProviderTarget

router = APIRouter(tags=["runs"])


def _build_evaluator(spec: EvaluatorSpec) -> Evaluator:
    params = spec.params
    match spec.name:
        case "exact_match":
            return ExactMatch(
                case_sensitive=bool(params.get("case_sensitive", False)),
                strip=bool(params.get("strip", True)),
            )
        case "regex_match":
            pattern = params.get("pattern")
            if not isinstance(pattern, str):
                raise HTTPException(status_code=400, detail="regex_match requires a 'pattern'")
            return RegexMatch(pattern, flags=int(params.get("flags", 0)))
        case "json_schema":
            schema = params.get("schema")
            if not isinstance(schema, dict):
                raise HTTPException(status_code=400, detail="json_schema requires a 'schema'")
            return JsonSchema(schema)
        case "llm_judge":
            try:
                judge_provider = make_provider(str(params.get("provider", "mock")))
            except KeyError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            return LLMJudge(
                judge_provider,
                rubric=str(params.get("rubric", "")),
                threshold=float(params.get("threshold", 0.5)),
                config=ProviderConfig(model=str(params.get("model", "mock"))),
            )
        case _:
            raise HTTPException(status_code=400, detail=f"unknown evaluator: {spec.name}")


def _serialize_metrics(metrics: RunMetrics) -> dict[str, object]:
    ci = metrics.success_rate_ci
    return {
        "total": metrics.total,
        "passed": metrics.passed,
        "errors": metrics.errors,
        "success_rate": metrics.success_rate,
        "success_rate_ci": {
            "point": ci.point,
            "low": ci.low,
            "high": ci.high,
            "confidence": ci.confidence,
        },
        "latency_p50": metrics.latency_p50,
        "latency_p95": metrics.latency_p95,
        "latency_mean": metrics.latency_mean,
        "total_cost": metrics.total_cost,
        "evaluator_pass_rates": metrics.evaluator_pass_rates,
        "repeat_success_mean": metrics.repeat_success_mean,
        "repeat_success_std": metrics.repeat_success_std,
    }


async def _read_run(db: AsyncSession, run_id: uuid.UUID) -> RunRead:
    run = await db.get(EvalRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    result = await db.execute(
        select(CaseResult)
        .where(CaseResult.eval_run_id == run_id)
        .order_by(CaseResult.repeat_index, CaseResult.created_at)
    )
    results = [
        CaseResultRead(
            test_case_id=cr.test_case_id,
            repeat_index=cr.repeat_index,
            output=cr.output,
            latency_ms=cr.latency_ms,
            passed=cr.passed,
            scores=cr.scores,
            error=cr.error,
        )
        for cr in result.scalars().all()
    ]
    return RunRead(
        id=run.id,
        project_id=run.project_id,
        dataset_id=run.dataset_id,
        status=run.status,
        repeats=run.repeats,
        aggregates=run.aggregates,
        error=run.error,
        results=results,
    )


@router.post(
    "/datasets/{dataset_id}/runs",
    response_model=RunRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_run(dataset_id: uuid.UUID, payload: RunCreate, db: DbSession) -> RunRead:
    dataset = await db.get(Dataset, dataset_id)
    if dataset is None or dataset.is_deleted:
        raise HTTPException(status_code=404, detail="dataset not found")

    case_rows = list(
        (
            await db.execute(
                select(TestCase)
                .where(TestCase.dataset_id == dataset_id)
                .order_by(TestCase.created_at, TestCase.id)
            )
        )
        .scalars()
        .all()
    )
    if not case_rows:
        raise HTTPException(status_code=400, detail="dataset has no test cases")

    eval_cases = [
        EvalCase(input=tc.input, expected=tc.expected, metadata=tc.case_metadata)
        for tc in case_rows
    ]
    evaluators = [_build_evaluator(spec) for spec in payload.evaluators]

    try:
        provider = make_provider(payload.provider)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    config = ProviderConfig(
        model=payload.model,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
        seed=payload.seed,
    )
    target = ProviderTarget(provider, config)

    run = EvalRun(
        project_id=dataset.project_id,
        dataset_id=dataset_id,
        status=RunStatus.RUNNING,
        repeats=payload.repeats,
        target_config={
            "provider": payload.provider,
            "model": payload.model,
            "temperature": payload.temperature,
            "max_tokens": payload.max_tokens,
            "seed": payload.seed,
        },
        evaluator_config=[spec.model_dump() for spec in payload.evaluators],
        started_at=datetime.now(UTC),
    )
    db.add(run)
    await db.flush()

    runner = EvalRunner(require_all=True)
    outcome = await runner.run(target, eval_cases, evaluators, repeats=payload.repeats)
    assert outcome.metrics is not None

    for record in outcome.records:
        source_case = case_rows[record.case_index]
        db.add(
            CaseResult(
                eval_run_id=run.id,
                test_case_id=source_case.id,
                repeat_index=record.repeat_index,
                output=record.output,
                latency_ms=record.latency_ms,
                passed=record.passed,
                scores=record.scores,
                error=record.error,
            )
        )

    run.status = RunStatus.COMPLETED
    run.finished_at = datetime.now(UTC)
    run.aggregates = _serialize_metrics(outcome.metrics)
    await db.commit()
    return await _read_run(db, run.id)


@router.get("/runs/{run_id}", response_model=RunRead)
async def get_run(run_id: uuid.UUID, db: DbSession) -> RunRead:
    return await _read_run(db, run_id)


@router.get("/datasets/{dataset_id}/runs", response_model=list[RunSummaryRead])
async def list_runs(dataset_id: uuid.UUID, db: DbSession) -> list[RunSummaryRead]:
    result = await db.execute(
        select(EvalRun).where(EvalRun.dataset_id == dataset_id).order_by(EvalRun.created_at.desc())
    )
    summaries: list[RunSummaryRead] = []
    for run in result.scalars().all():
        success_rate = run.aggregates.get("success_rate")
        summaries.append(
            RunSummaryRead(
                id=run.id,
                dataset_id=run.dataset_id,
                status=run.status,
                success_rate=(
                    float(success_rate) if isinstance(success_rate, (int, float)) else None
                ),
                created_at=run.created_at,
            )
        )
    return summaries
