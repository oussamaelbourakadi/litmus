"""EvalRunner — execute a target over a dataset and score each output.

Per-case isolation: a failure in one case (target or evaluator) is recorded and
does not stop the run. The case verdict is the AND of all evaluators by default.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field

from app.engine.metrics import CaseOutcome, RunMetrics, compute_metrics
from app.engine.retry import RetryPolicy, with_retries
from app.evaluators.base import EvalCase, Evaluator
from app.targets.base import Target, TargetResponse

logger = logging.getLogger("litmus.engine")


def _as_int(value: object) -> int:
    return value if isinstance(value, int) else 0


def _as_str(value: object) -> str:
    return value if isinstance(value, str) else ""


@dataclass(slots=True)
class CaseRecord:
    case_index: int
    repeat_index: int
    output: str
    latency_ms: float
    passed: bool
    scores: dict[str, dict[str, object]]
    error: str | None = None


@dataclass(slots=True)
class RunOutcome:
    records: list[CaseRecord] = field(default_factory=list)
    metrics: RunMetrics | None = None
    cancelled: bool = False


# Called after each completed case: (record, outcome, completed_count, total_count).
OnCase = Callable[[CaseRecord, CaseOutcome, int, int], Awaitable[None]]
# Checked before each case; returning True stops the run early (cooperative cancel).
ShouldCancel = Callable[[], bool]


class EvalRunner:
    def __init__(
        self,
        *,
        require_all: bool = True,
        bootstrap_seed: int = 1234,
        concurrency: int = 1,
        case_timeout: float = 60.0,
        retry_policy: RetryPolicy | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._require_all = require_all
        self._bootstrap_seed = bootstrap_seed
        self._concurrency = max(1, concurrency)
        self._case_timeout = case_timeout
        self._retry_policy = retry_policy or RetryPolicy()
        self._sleep = sleep

    async def run(
        self,
        target: Target,
        cases: Sequence[EvalCase],
        evaluators: Sequence[Evaluator],
        *,
        repeats: int = 1,
        on_case: OnCase | None = None,
        should_cancel: ShouldCancel | None = None,
    ) -> RunOutcome:
        records: list[CaseRecord] = []
        outcomes: list[CaseOutcome] = []
        total = len(cases) * repeats
        completed = 0
        cancelled = False

        work = iter(
            (case_index, repeat_index, case)
            for repeat_index in range(repeats)
            for case_index, case in enumerate(cases)
        )
        in_flight: set[asyncio.Task[tuple[CaseRecord, CaseOutcome]]] = set()

        def schedule_more() -> None:
            nonlocal cancelled
            while len(in_flight) < self._concurrency:
                if should_cancel is not None and should_cancel():
                    cancelled = True
                    return
                try:
                    case_index, repeat_index, case = next(work)
                except StopIteration:
                    return
                in_flight.add(
                    asyncio.create_task(
                        self._run_one(target, case, evaluators, case_index, repeat_index)
                    )
                )

        schedule_more()
        while in_flight:
            done, _ = await asyncio.wait(in_flight, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                in_flight.discard(task)
                record, outcome = task.result()
                records.append(record)
                outcomes.append(outcome)
                completed += 1
                if on_case is not None:
                    await on_case(record, outcome, completed, total)
            if not cancelled:
                schedule_more()

        metrics = compute_metrics(outcomes, repeats=repeats, bootstrap_seed=self._bootstrap_seed)
        logger.info(
            "run finished: %d/%d cases, %d errors, cancelled=%s",
            completed,
            total,
            metrics.errors,
            cancelled,
        )
        return RunOutcome(records=records, metrics=metrics, cancelled=cancelled)

    async def _invoke_target(self, target: Target, prompt: str) -> TargetResponse:
        """Call the target with a per-attempt timeout and transient-error retries."""

        async def _call() -> TargetResponse:
            async with asyncio.timeout(self._case_timeout):
                return await target.run(prompt)

        return await with_retries(_call, self._retry_policy, sleep=self._sleep)

    async def _run_one(
        self,
        target: Target,
        case: EvalCase,
        evaluators: Sequence[Evaluator],
        case_index: int,
        repeat_index: int,
    ) -> tuple[CaseRecord, CaseOutcome]:
        try:
            response = await self._invoke_target(target, case.input)
        except Exception as exc:  # per-case isolation (after retries/timeout)
            logger.warning("case %d failed at target: %s", case_index, exc)
            record = CaseRecord(case_index, repeat_index, "", 0.0, False, {}, str(exc))
            outcome = CaseOutcome(
                passed=False,
                latency_ms=0.0,
                prompt_tokens=0,
                completion_tokens=0,
                evaluator_passed={},
                model="",
                repeat_index=repeat_index,
                errored=True,
            )
            return record, outcome

        scores: dict[str, dict[str, object]] = {}
        evaluator_passed: dict[str, bool] = {}
        for evaluator in evaluators:
            try:
                score = await evaluator.score(case, response.output)
            except Exception as exc:  # a broken evaluator must not sink the run
                scores[evaluator.name] = {
                    "value": 0.0,
                    "passed": False,
                    "reason": f"evaluator error: {exc}",
                }
                evaluator_passed[evaluator.name] = False
                continue
            scores[evaluator.name] = {
                "value": score.value,
                "passed": score.passed,
                "reason": score.reason,
            }
            evaluator_passed[evaluator.name] = score.passed

        if evaluator_passed:
            verdicts = evaluator_passed.values()
            passed = all(verdicts) if self._require_all else any(verdicts)
        else:
            passed = False

        outcome = CaseOutcome(
            passed=passed,
            latency_ms=response.latency_ms,
            prompt_tokens=_as_int(response.metadata.get("prompt_tokens")),
            completion_tokens=_as_int(response.metadata.get("completion_tokens")),
            evaluator_passed=evaluator_passed,
            model=_as_str(response.metadata.get("model")),
            repeat_index=repeat_index,
        )
        record = CaseRecord(
            case_index=case_index,
            repeat_index=repeat_index,
            output=response.output,
            latency_ms=response.latency_ms,
            passed=passed,
            scores=scores,
        )
        return record, outcome
