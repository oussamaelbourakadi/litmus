"""Evaluators.

Concrete evaluators (ExactMatch, RegexMatch, JsonSchema, LLMJudge) land in
Phase 1.2. This package already exposes the :class:`Evaluator` interface and the
shared ``evaluator_registry`` so those implementations plug in without touching
the engine.
"""

from __future__ import annotations

from app.evaluators.base import EvalScore, Evaluator, evaluator_registry

__all__ = ["EvalScore", "Evaluator", "evaluator_registry"]
