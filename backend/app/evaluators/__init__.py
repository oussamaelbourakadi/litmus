"""Evaluators.

Importing this package registers every concrete evaluator on
``evaluator_registry``. Adding an evaluator = a class + ``@register`` decorator,
with no change to the engine.
"""

from __future__ import annotations

from app.evaluators.base import EvalCase, EvalScore, Evaluator, evaluator_registry
from app.evaluators.calibration import cohen_kappa, judge_agreement
from app.evaluators.exact_match import ExactMatch
from app.evaluators.json_schema import JsonSchema
from app.evaluators.llm_judge import LLMJudge
from app.evaluators.regex_match import RegexMatch

__all__ = [
    "EvalCase",
    "EvalScore",
    "Evaluator",
    "ExactMatch",
    "JsonSchema",
    "LLMJudge",
    "RegexMatch",
    "cohen_kappa",
    "evaluator_registry",
    "judge_agreement",
]
