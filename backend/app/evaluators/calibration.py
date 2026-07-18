"""Judge calibration: measure agreement between an evaluator and human labels.

This makes the "calibration measured" claim concrete and honest: given a set of
cases with human pass/fail labels, we report the evaluator's agreement (accuracy)
and Cohen's kappa (chance-corrected agreement). Deterministic when the evaluator
uses the MockProvider.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.evaluators.base import EvalCase, Evaluator


async def judge_agreement(
    evaluator: Evaluator,
    cases: Sequence[tuple[EvalCase, str]],
    human_labels: Sequence[bool],
) -> float:
    """Fraction of cases where the evaluator's verdict matches the human label."""
    if len(cases) != len(human_labels):
        raise ValueError("cases and human_labels must have the same length")
    if not cases:
        return 0.0

    agreements = 0
    for (case, output), label in zip(cases, human_labels, strict=True):
        score = await evaluator.score(case, output)
        if score.passed == label:
            agreements += 1
    return agreements / len(cases)


def cohen_kappa(a: Sequence[bool], b: Sequence[bool]) -> float:
    """Cohen's kappa for two binary label sequences."""
    if len(a) != len(b):
        raise ValueError("label sequences must have the same length")
    n = len(a)
    if n == 0:
        return 0.0

    observed = sum(1 for x, y in zip(a, b, strict=True) if x == y) / n
    p_a = sum(a) / n
    p_b = sum(b) / n
    expected = p_a * p_b + (1 - p_a) * (1 - p_b)
    if expected >= 1.0:
        return 1.0
    return (observed - expected) / (1 - expected)
