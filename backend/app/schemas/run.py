"""Run DTOs."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EvaluatorSpec(BaseModel):
    name: str
    params: dict[str, Any] = Field(default_factory=dict)


class RunCreate(BaseModel):
    provider: str = "mock"
    model: str = "mock"
    temperature: float = 0.0
    max_tokens: int = Field(default=512, ge=1)
    seed: int | None = 0
    repeats: int = Field(default=1, ge=1, le=50)
    evaluators: list[EvaluatorSpec] = Field(
        default_factory=lambda: [EvaluatorSpec(name="exact_match")]
    )


class CaseResultRead(BaseModel):
    test_case_id: uuid.UUID
    repeat_index: int
    output: str
    latency_ms: float
    passed: bool
    scores: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class RunRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    dataset_id: uuid.UUID
    status: str
    repeats: int
    total_cases: int = 0
    completed_cases: int = 0
    aggregates: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    results: list[CaseResultRead] = Field(default_factory=list)


class RunStatusRead(BaseModel):
    id: uuid.UUID
    status: str
    total_cases: int
    completed_cases: int
    error: str | None = None


class RunSummaryRead(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    status: str
    success_rate: float | None = None
    created_at: datetime
