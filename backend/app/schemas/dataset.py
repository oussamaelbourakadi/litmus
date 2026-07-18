"""Dataset and test-case DTOs."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field


class TestCaseCreate(BaseModel):
    input: str
    expected: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DatasetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    cases: list[TestCaseCreate] = Field(default_factory=list)


class TestCaseRead(BaseModel):
    id: uuid.UUID
    input: str
    expected: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DatasetRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    description: str | None = None
    cases: list[TestCaseRead] = Field(default_factory=list)
