"""Comparison DTOs."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class ThresholdSpec(BaseModel):
    mode: str = "absolute"
    max_drop: float = 0.0


class CompareRequest(BaseModel):
    base_run_id: uuid.UUID
    candidate_run_id: uuid.UUID
    threshold: ThresholdSpec = Field(default_factory=ThresholdSpec)


class CaseChangeRead(BaseModel):
    test_case_id: str
    base_pass_rate: float
    candidate_pass_rate: float
    status: str


class VerdictRead(BaseModel):
    passed: bool
    reason: str


class RunComparisonRead(BaseModel):
    base_run_id: uuid.UUID
    candidate_run_id: uuid.UUID
    success_rate_base: float
    success_rate_candidate: float
    success_rate_delta: float
    latency_p50_delta: float
    latency_p95_delta: float
    cost_delta: float
    regressions: int
    improvements: int
    case_changes: list[CaseChangeRead]
    verdict: VerdictRead
