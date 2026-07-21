"""Bounded-concurrency runner tests."""

from __future__ import annotations

import asyncio

from app.engine.runner import EvalRunner
from app.evaluators.base import EvalCase
from app.evaluators.exact_match import ExactMatch
from app.targets.base import Target, TargetResponse


class CountingTarget(Target):
    """Tracks the maximum number of concurrently in-flight calls."""

    def __init__(self) -> None:
        self.in_flight = 0
        self.max_in_flight = 0

    async def run(self, input: str) -> TargetResponse:
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        await asyncio.sleep(0.01)
        self.in_flight -= 1
        return TargetResponse(output=input, latency_ms=1.0, metadata={"model": "t"})


def _cases(n: int) -> list[EvalCase]:
    return [EvalCase(input=f"q{i}", expected=f"q{i}") for i in range(n)]


async def test_concurrency_is_bounded_and_used() -> None:
    target = CountingTarget()
    outcome = await EvalRunner(concurrency=4).run(target, _cases(20), [ExactMatch()])
    assert outcome.metrics is not None
    assert outcome.metrics.total == 20
    assert outcome.metrics.success_rate == 1.0
    assert 2 <= target.max_in_flight <= 4


async def test_metrics_match_sequential() -> None:
    seq = await EvalRunner(concurrency=1).run(CountingTarget(), _cases(10), [ExactMatch()])
    conc = await EvalRunner(concurrency=5).run(CountingTarget(), _cases(10), [ExactMatch()])
    assert seq.metrics is not None
    assert conc.metrics is not None
    assert seq.metrics.total == conc.metrics.total == 10
    assert seq.metrics.success_rate == conc.metrics.success_rate == 1.0


async def test_case_timeout_isolates_slow_call() -> None:
    class SlowTarget(Target):
        async def run(self, input: str) -> TargetResponse:
            await asyncio.sleep(0.2)
            return TargetResponse(output=input, latency_ms=1.0, metadata={})

    outcome = await EvalRunner(case_timeout=0.02).run(
        SlowTarget(), [EvalCase(input="a", expected="a")], [ExactMatch()]
    )
    assert outcome.metrics is not None
    assert outcome.metrics.errors == 1
    assert outcome.records[0].error is not None
