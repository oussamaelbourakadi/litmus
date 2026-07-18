"""Comparison endpoint: diff two runs and render a regression verdict."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.engine.compare import RunSummary, ThresholdConfig, compare_runs
from app.models.case_result import CaseResult
from app.models.eval_run import EvalRun
from app.schemas.compare import (
    CaseChangeRead,
    CompareRequest,
    RunComparisonRead,
    VerdictRead,
)

router = APIRouter(tags=["compare"])


def _as_float(value: object) -> float:
    return float(value) if isinstance(value, (int, float)) else 0.0


async def _run_summary(db: AsyncSession, run_id: uuid.UUID) -> RunSummary:
    run = await db.get(EvalRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"run {run_id} not found")

    result = await db.execute(select(CaseResult).where(CaseResult.eval_run_id == run_id))
    by_case: dict[str, list[bool]] = {}
    for case_result in result.scalars().all():
        by_case.setdefault(str(case_result.test_case_id), []).append(case_result.passed)
    case_pass_rates = {
        case_id: sum(1 for passed in flags if passed) / len(flags)
        for case_id, flags in by_case.items()
    }

    aggregates = run.aggregates
    return RunSummary(
        run_id=str(run.id),
        success_rate=_as_float(aggregates.get("success_rate")),
        latency_p50=_as_float(aggregates.get("latency_p50")),
        latency_p95=_as_float(aggregates.get("latency_p95")),
        total_cost=_as_float(aggregates.get("total_cost")),
        case_pass_rates=case_pass_rates,
    )


@router.post("/compare", response_model=RunComparisonRead)
async def compare(payload: CompareRequest, db: DbSession) -> RunComparisonRead:
    base = await _run_summary(db, payload.base_run_id)
    candidate = await _run_summary(db, payload.candidate_run_id)
    threshold = ThresholdConfig(mode=payload.threshold.mode, max_drop=payload.threshold.max_drop)
    comparison = compare_runs(base, candidate, threshold)

    return RunComparisonRead(
        base_run_id=payload.base_run_id,
        candidate_run_id=payload.candidate_run_id,
        success_rate_base=comparison.success_rate_base,
        success_rate_candidate=comparison.success_rate_candidate,
        success_rate_delta=comparison.success_rate_delta,
        latency_p50_delta=comparison.latency_p50_delta,
        latency_p95_delta=comparison.latency_p95_delta,
        cost_delta=comparison.cost_delta,
        regressions=comparison.regressions,
        improvements=comparison.improvements,
        case_changes=[
            CaseChangeRead(
                test_case_id=change.test_case_id,
                base_pass_rate=change.base_pass_rate,
                candidate_pass_rate=change.candidate_pass_rate,
                status=change.status,
            )
            for change in comparison.case_changes
        ],
        verdict=VerdictRead(passed=comparison.verdict.passed, reason=comparison.verdict.reason),
    )
