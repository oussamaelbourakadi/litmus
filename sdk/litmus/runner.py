"""Local, serverless run loop with per-case error isolation.

A target is any callable ``str -> str`` (the system under test). Helpers build one
from a Python entrypoint (``module:function``) or an HTTP endpoint.
"""

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from time import perf_counter
from typing import Any

import httpx

from litmus.evaluators import Evaluator
from litmus.metrics import summarize
from litmus.models import Case, CaseResult, RunResult, Score

Target = Callable[[str], str]


def python_target(entrypoint: str, *, search_path: Path | None = None) -> Target:
    """Load a ``module:function`` callable, optionally adding a directory to sys.path."""
    if ":" not in entrypoint:
        raise ValueError("python target entrypoint must be 'module:function'")
    module_name, func_name = entrypoint.split(":", 1)
    if search_path is not None:
        path_str = str(search_path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
        # Force a fresh import from search_path (avoids stale module cache).
        sys.modules.pop(module_name, None)
    module = importlib.import_module(module_name)
    func: Any = getattr(module, func_name)
    if not callable(func):
        raise ValueError(f"{entrypoint} is not callable")
    return lambda prompt: str(func(prompt))


def http_target(url: str, *, input_field: str = "input", output_field: str = "output") -> Target:
    """Build a target that POSTs the input and reads a field from the JSON response."""

    def call(prompt: str) -> str:
        response = httpx.post(url, json={input_field: prompt}, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        return str(data[output_field])

    return call


def run_local(
    cases: Sequence[Case],
    target: Target,
    evaluators: Sequence[Evaluator],
    *,
    repeats: int = 1,
    seed: int = 1234,
    require_all: bool = True,
) -> RunResult:
    results: list[CaseResult] = []
    for repeat_index in range(repeats):
        for case in cases:
            results.append(_run_one(case, target, evaluators, repeat_index, require_all))
    return summarize(results, seed=seed)


def _run_one(
    case: Case,
    target: Target,
    evaluators: Sequence[Evaluator],
    repeat_index: int,
    require_all: bool,
) -> CaseResult:
    start = perf_counter()
    try:
        output = target(case.input)
    except Exception as exc:  # per-case isolation
        return CaseResult(
            input=case.input,
            output="",
            latency_ms=(perf_counter() - start) * 1000,
            passed=False,
            scores=[],
            repeat_index=repeat_index,
            error=str(exc),
        )
    latency_ms = (perf_counter() - start) * 1000

    scores: list[Score] = []
    for evaluator in evaluators:
        try:
            scores.append(evaluator.score(case, output))
        except Exception as exc:
            scores.append(Score(evaluator.name, 0.0, False, f"evaluator error: {exc}"))

    if scores:
        verdicts = [s.passed for s in scores]
        passed = all(verdicts) if require_all else any(verdicts)
    else:
        passed = False

    return CaseResult(
        input=case.input,
        output=output,
        latency_ms=latency_ms,
        passed=passed,
        scores=scores,
        repeat_index=repeat_index,
    )
