"""Pure data models for the SDK (no third-party dependencies)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Case:
    input: str
    expected: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class Score:
    name: str
    value: float
    passed: bool
    reason: str | None = None


@dataclass(slots=True)
class CaseResult:
    input: str
    output: str
    latency_ms: float
    passed: bool
    scores: list[Score]
    repeat_index: int = 0
    error: str | None = None


@dataclass(slots=True)
class RunResult:
    results: list[CaseResult]
    total: int
    passed: int
    errors: int
    success_rate: float
    ci_low: float
    ci_high: float
    latency_p50: float
    latency_p95: float


@dataclass(slots=True)
class Threshold:
    mode: str = "absolute"  # "absolute" | "relative"
    max_drop: float = 0.0


@dataclass(slots=True)
class Comparison:
    base_success: float
    candidate_success: float
    delta: float
    passed: bool
    reason: str
