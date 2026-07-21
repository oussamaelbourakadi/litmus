"""Run endpoints: launch an evaluation run (async, in the background) and read it.

`create_run` validates the request, persists a pending run, and schedules an
in-process background task to execute it; results and progress are polled via
`GET /runs/{id}` (or the lightweight `/status`), and a run can be cancelled.
Durable, resumable execution via a Redis worker arrives in sub-phase 1.8.2.
"""

from __future__ import annotations

import asyncio
import uuid

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.engine.execution import execute_run
from app.evaluators.base import Evaluator
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
    RunStatusRead,
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
        total_cases=run.total_cases,
        completed_cases=run.completed_cases,
        aggregates=run.aggregates,
        error=run.error,
        results=results,
    )


@router.post(
    "/datasets/{dataset_id}/runs",
    response_model=RunRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_run(
    dataset_id: uuid.UUID, payload: RunCreate, request: Request, db: DbSession
) -> RunRead:
    dataset = await db.get(Dataset, dataset_id)
    if dataset is None or dataset.is_deleted:
        raise HTTPException(status_code=404, detail="dataset not found")

    case_count = await db.scalar(
        select(func.count(TestCase.id)).where(TestCase.dataset_id == dataset_id)
    )
    if not case_count:
        raise HTTPException(status_code=400, detail="dataset has no test cases")

    # Build target + evaluators now so bad specs fail fast with a 400.
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
        status=RunStatus.PENDING,
        repeats=payload.repeats,
        total_cases=case_count * payload.repeats,
        target_config={
            "provider": payload.provider,
            "model": payload.model,
            "temperature": payload.temperature,
            "max_tokens": payload.max_tokens,
            "seed": payload.seed,
        },
        evaluator_config=[spec.model_dump() for spec in payload.evaluators],
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    state = request.app.state
    task = asyncio.create_task(
        execute_run(
            run.id,
            target,
            evaluators,
            payload.repeats,
            session_factory=state.run_session_factory,
            cancellations=state.cancellations,
        )
    )
    state.run_tasks.add(task)
    task.add_done_callback(state.run_tasks.discard)

    return await _read_run(db, run.id)


@router.get("/runs/{run_id}", response_model=RunRead)
async def get_run(run_id: uuid.UUID, db: DbSession) -> RunRead:
    return await _read_run(db, run_id)


@router.get("/runs/{run_id}/status", response_model=RunStatusRead)
async def get_run_status(run_id: uuid.UUID, db: DbSession) -> RunStatusRead:
    run = await db.get(EvalRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return RunStatusRead(
        id=run.id,
        status=run.status,
        total_cases=run.total_cases,
        completed_cases=run.completed_cases,
        error=run.error,
    )


@router.post("/runs/{run_id}/cancel", response_model=RunStatusRead)
async def cancel_run(run_id: uuid.UUID, request: Request, db: DbSession) -> RunStatusRead:
    run = await db.get(EvalRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    if run.status not in RunStatus.TERMINAL:
        request.app.state.cancellations.request(run_id)
        run.cancel_requested = True
        await db.commit()
    return RunStatusRead(
        id=run.id,
        status=run.status,
        total_cases=run.total_cases,
        completed_cases=run.completed_cases,
        error=run.error,
    )


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
