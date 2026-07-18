"""ExactMatch — normalized equality between output and expected reference."""

from __future__ import annotations

from app.evaluators.base import EvalCase, EvalScore, Evaluator, evaluator_registry


@evaluator_registry.register("exact_match")
class ExactMatch(Evaluator):
    name = "exact_match"

    def __init__(self, *, case_sensitive: bool = False, strip: bool = True) -> None:
        self._case_sensitive = case_sensitive
        self._strip = strip

    async def score(self, case: EvalCase, output: str) -> EvalScore:
        if case.expected is None:
            return EvalScore(0.0, False, "no expected value provided")
        passed = self._normalize(output) == self._normalize(case.expected)
        reason = None if passed else f"expected {case.expected!r}, got {output!r}"
        return EvalScore(1.0 if passed else 0.0, passed, reason)

    def _normalize(self, text: str) -> str:
        if self._strip:
            text = text.strip()
        if not self._case_sensitive:
            text = text.casefold()
        return text
