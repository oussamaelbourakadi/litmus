"""Background run execution: incremental persistence, progress, cancellation.

For sub-phase 1.8.0 a run executes as an in-process asyncio task. It owns its own
DB session (not the request's), persists each ``CaseResult`` as it completes,
updates progress, and stops cooperatively when cancellation is requested.

NOTE: in-process tasks are **not durable across a server restart** — durable,
resumable execution via a Redis worker (arq) arrives in sub-phase 1.8.2.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.engine.metrics import CaseOutcome, serialize_metrics
from app.engine.runner import CaseRecord, EvalRunner
from app.evaluators.base import EvalCase, Evaluator
from app.models.case_result import CaseResult
from app.models.eval_run import EvalRun, RunStatus
from app.models.test_case import TestCase
from app.targets.base import Target

logger = logging.getLogger("litmus.execution")

SessionFactory = async_sessionmaker[AsyncSession]


class CancellationRegistry:
    """In-memory set of run ids whose cancellation has been requested."""

    def __init__(self) -> None:
        self._cancelled: set[uuid.UUID] = set()

    def request(self, run_id: uuid.UUID) -> None:
        self._cancelled.add(run_id)

    def is_cancelled(self, run_id: uuid.UUID) -> bool:
        return run_id in self._cancelled

    def clear(self, run_id: uuid.UUID) -> None:
        self._cancelled.discard(run_id)


async def execute_run(
    run_id: uuid.UUID,
    target: Target,
    evaluators: list[Evaluator],
    repeats: int,
    *,
    session_factory: SessionFactory,
    cancellations: CancellationRegistry,
) -> None:
    """Execute a persisted run in the background and record its outcome."""
    async with session_factory() as db:
        run = await db.get(EvalRun, run_id)
        if run is None:
            logger.warning("run %s vanished before execution", run_id)
            cancellations.clear(run_id)
            return

        case_rows = list(
            (
                await db.execute(
                    select(TestCase)
                    .where(TestCase.dataset_id == run.dataset_id)
                    .order_by(TestCase.created_at, TestCase.id)
                )
            )
            .scalars()
            .all()
        )
        eval_cases = [
            EvalCase(input=tc.input, expected=tc.expected, metadata=tc.case_metadata)
            for tc in case_rows
        ]

        run.status = RunStatus.RUNNING
        run.started_at = datetime.now(UTC)
        await db.commit()

        async def on_case(record: CaseRecord, _: CaseOutcome, completed: int, __: int) -> None:
            source = case_rows[record.case_index]
            db.add(
                CaseResult(
                    eval_run_id=run.id,
                    test_case_id=source.id,
                    repeat_index=record.repeat_index,
                    output=record.output,
                    latency_ms=record.latency_ms,
                    passed=record.passed,
                    scores=record.scores,
                    error=record.error,
                )
            )
            run.completed_cases = completed
            await db.commit()

        def should_cancel() -> bool:
            return cancellations.is_cancelled(run_id)

        try:
            outcome = await EvalRunner(require_all=True).run(
                target,
                eval_cases,
                evaluators,
                repeats=repeats,
                on_case=on_case,
                should_cancel=should_cancel,
            )
        except Exception as exc:  # a whole-run failure must be recorded, not swallowed
            logger.exception("run %s failed", run_id)
            run.status = RunStatus.FAILED
            run.error = str(exc)
            run.finished_at = datetime.now(UTC)
            await db.commit()
            cancellations.clear(run_id)
            return

        assert outcome.metrics is not None
        run.status = RunStatus.CANCELLED if outcome.cancelled else RunStatus.COMPLETED
        run.aggregates = serialize_metrics(outcome.metrics)
        run.finished_at = datetime.now(UTC)
        await db.commit()

    cancellations.clear(run_id)
