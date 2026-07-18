"""Project model — root of the Phase 1 (EVALUATE) data model."""

from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin


class Project(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    """A workspace that owns datasets, evaluation runs and (later) red-team runs."""

    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Project(id={self.id!r}, slug={self.slug!r})"
