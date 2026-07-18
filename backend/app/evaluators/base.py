"""Evaluator interface and registry (Phase 1.0 seed).

An evaluator scores a model ``output`` against an expected reference and returns
a normalized score in [0, 1] plus a pass/fail verdict and an optional reason.

The signature is intentionally minimal for the scaffold; in Phase 1.2 it will
accept the full ``TestCase`` model (which does not exist yet) instead of a bare
``expected`` string.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.registry import Registry


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
    def score(self, output: str, expected: str | None = None) -> EvalScore:
        """Score ``output`` against ``expected``."""
        raise NotImplementedError


evaluator_registry: Registry[Evaluator] = Registry("evaluator")
