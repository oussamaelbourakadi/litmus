"""ORM models.

Importing this package registers every table on ``Base.metadata`` — Alembic's
``env.py`` imports it so autogenerate and migrations see the full schema.
"""

from __future__ import annotations

from app.models.project import Project

__all__ = ["Project"]
