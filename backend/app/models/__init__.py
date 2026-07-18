"""ORM models.

Importing this package registers every table on ``Base.metadata`` — Alembic's
``env.py`` imports it so autogenerate and migrations see the full schema.
"""

from __future__ import annotations

from app.models.case_result import CaseResult
from app.models.dataset import Dataset
from app.models.eval_run import EvalRun, RunStatus
from app.models.project import Project
from app.models.test_case import TestCase

__all__ = [
    "CaseResult",
    "Dataset",
    "EvalRun",
    "Project",
    "RunStatus",
    "TestCase",
]
