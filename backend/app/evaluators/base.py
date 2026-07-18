"""Evaluator interface and registry.

An evaluator scores a model ``output`` for a given :class:`EvalCase` and returns
a normalized score in [0, 1] plus a pass/fail verdict and an optional reason.

``score`` is async so the runner (1.3) can await every evaluator uniformly;
deterministic evaluators simply never await, while :class:`LLMJudge` awaits a
provider. ``EvalCase`` is a lightweight, non-ORM input; the persisted
``TestCase`` model (1.3) maps onto it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.core.registry import Registry


@dataclass(slots=True)
class EvalCase:
    """A single case to evaluate."""

    input: str
    expected: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class EvalScore:
    """Outcome of scoring a single case."""

    value: float
    passed: bool
    reason: str | None = None


class Evaluator(ABC):
    """Abstract evaluator plugin."""

    name: str = "base"

    @abstractmethod
    async def score(self, case: EvalCase, output: str) -> EvalScore:
        """Score ``output`` for ``case``."""
        raise NotImplementedError


evaluator_registry: Registry[Evaluator] = Registry("evaluator")
