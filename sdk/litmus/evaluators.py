"""Lightweight, self-contained evaluators for the serverless gate.

These mirror the semantics of the backend evaluators but carry no heavy
dependencies, so the CLI runs anywhere with just the SDK installed.
"""

from __future__ import annotations

import re
from typing import Protocol

from litmus.models import Case, Score


class Evaluator(Protocol):
    name: str

    def score(self, case: Case, output: str) -> Score: ...


class ExactMatch:
    name = "exact_match"

    def __init__(self, *, case_sensitive: bool = False, strip: bool = True) -> None:
        self._case_sensitive = case_sensitive
        self._strip = strip

    def score(self, case: Case, output: str) -> Score:
        if case.expected is None:
            return Score(self.name, 0.0, False, "no expected value")
        passed = self._normalize(output) == self._normalize(case.expected)
        return Score(self.name, 1.0 if passed else 0.0, passed)

    def _normalize(self, text: str) -> str:
        if self._strip:
            text = text.strip()
        if not self._case_sensitive:
            text = text.casefold()
        return text


class RegexMatch:
    name = "regex_match"

    def __init__(self, pattern: str, *, flags: int = 0) -> None:
        self._pattern = re.compile(pattern, flags)

    def score(self, case: Case, output: str) -> Score:
        passed = self._pattern.search(output) is not None
        return Score(self.name, 1.0 if passed else 0.0, passed)


class Contains:
    name = "contains"

    def __init__(self, substring: str, *, case_sensitive: bool = False) -> None:
        self._substring = substring if case_sensitive else substring.casefold()
        self._case_sensitive = case_sensitive

    def score(self, case: Case, output: str) -> Score:
        haystack = output if self._case_sensitive else output.casefold()
        passed = self._substring in haystack
        return Score(self.name, 1.0 if passed else 0.0, passed)


def build_evaluator(spec: dict[str, object]) -> Evaluator:
    """Build an evaluator from a config spec like ``{"type": "regex_match", "pattern": "..."}``."""
    kind = str(spec.get("type", ""))
    if kind == "exact_match":
        return ExactMatch(
            case_sensitive=bool(spec.get("case_sensitive", False)),
            strip=bool(spec.get("strip", True)),
        )
    if kind == "regex_match":
        pattern = spec.get("pattern")
        if not isinstance(pattern, str):
            raise ValueError("regex_match requires a 'pattern'")
        return RegexMatch(pattern)
    if kind == "contains":
        substring = spec.get("substring")
        if not isinstance(substring, str):
            raise ValueError("contains requires a 'substring'")
        return Contains(substring)
    raise ValueError(f"unknown evaluator type: {kind!r}")
