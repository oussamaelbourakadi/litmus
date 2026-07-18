"""EvalRunner tests, including per-case error isolation."""

from __future__ import annotations

from app.engine.runner import EvalRunner
from app.evaluators.base import EvalCase
from app.evaluators.exact_match import ExactMatch
from app.providers.base import GenerateResult, ModelProvider, ProviderConfig
from app.providers.mock import MockProvider
from app.targets.provider_target import ProviderTarget


def _mock_target(responses: dict[str, str]) -> ProviderTarget:
    return ProviderTarget(MockProvider(responses=responses), ProviderConfig(model="mock"))


async def test_basic_run_all_pass() -> None:
    target = _mock_target({"ping": "pong"})
    outcome = await EvalRunner().run(
        target, [EvalCase(input="ping", expected="pong")], [ExactMatch()]
    )
    assert outcome.metrics is not None
    assert outcome.metrics.total == 1
    assert outcome.metrics.success_rate == 1.0
    assert outcome.records[0].passed


async def test_case_error_is_isolated() -> None:
    class BoomProvider(ModelProvider):
        name = "boom"

        async def generate(self, prompt: str, config: ProviderConfig) -> GenerateResult:
            raise RuntimeError("boom")

    target = ProviderTarget(BoomProvider(), ProviderConfig())
    outcome = await EvalRunner().run(
        target, [EvalCase(input="a"), EvalCase(input="b")], [ExactMatch()]
    )
    assert outcome.metrics is not None
    assert outcome.metrics.total == 2
    assert outcome.metrics.errors == 2
    assert outcome.metrics.success_rate == 0.0
    assert outcome.records[0].error is not None


async def test_repeats_multiply_records() -> None:
    target = _mock_target({"ping": "pong"})
    outcome = await EvalRunner().run(
        target, [EvalCase(input="ping", expected="pong")], [ExactMatch()], repeats=3
    )
    assert len(outcome.records) == 3
    assert outcome.metrics is not None
    assert outcome.metrics.repeat_success_mean == 1.0


async def test_and_verdict_requires_all_evaluators() -> None:
    # Output "pong" matches exact but not the regex \d+, so AND fails.
    from app.evaluators.regex_match import RegexMatch

    target = _mock_target({"ping": "pong"})
    outcome = await EvalRunner().run(
        target,
        [EvalCase(input="ping", expected="pong")],
        [ExactMatch(), RegexMatch(r"\d+")],
    )
    assert outcome.records[0].passed is False
