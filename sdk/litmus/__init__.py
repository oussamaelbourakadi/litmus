"""Litmus SDK — evaluate AI systems locally and gate CI on regressions."""

from litmus.compare import compare
from litmus.evaluators import Contains, ExactMatch, RegexMatch, build_evaluator
from litmus.metrics import bootstrap_ci, summarize
from litmus.models import Case, CaseResult, Comparison, RunResult, Score, Threshold
from litmus.runner import run_local

__version__ = "0.1.0"

__all__ = [
    "Case",
    "CaseResult",
    "Comparison",
    "Contains",
    "ExactMatch",
    "RegexMatch",
    "RunResult",
    "Score",
    "Threshold",
    "bootstrap_ci",
    "build_evaluator",
    "compare",
    "run_local",
    "summarize",
]
