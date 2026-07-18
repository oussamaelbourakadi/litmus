"""TestCase model — a single input/expected pair inside a dataset."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin


class TestCase(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "test_cases"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), index=True
    )
    input: Mapped[str] = mapped_column(Text, nullable=False)
    expected: Mapped[str | None] = mapped_column(Text, nullable=True)
    case_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
