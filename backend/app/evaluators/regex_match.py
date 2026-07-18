"""RegexMatch — pass if a configurable pattern is found in the output."""

from __future__ import annotations

import re

from app.evaluators.base import EvalCase, EvalScore, Evaluator, evaluator_registry


@evaluator_registry.register("regex_match")
class RegexMatch(Evaluator):
    name = "regex_match"

    def __init__(self, pattern: str, *, flags: int = 0) -> None:
        self._pattern = re.compile(pattern, flags)

    async def score(self, case: EvalCase, output: str) -> EvalScore:
        passed = self._pattern.search(output) is not None
        reason = None if passed else f"pattern {self._pattern.pattern!r} not found in output"
        return EvalScore(1.0 if passed else 0.0, passed, reason)
