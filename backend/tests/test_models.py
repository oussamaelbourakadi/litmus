"""Model / mixin persistence tests."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


async def test_project_persists_with_mixins(db_session: AsyncSession) -> None:
    project = Project(name="Demo", slug="demo", description="a demo project")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    assert isinstance(project.id, uuid.UUID)
    assert isinstance(project.created_at, datetime)
    assert isinstance(project.updated_at, datetime)
    assert project.is_deleted is False
    assert project.deleted_at is None


async def test_project_roundtrip_query(db_session: AsyncSession) -> None:
    db_session.add(Project(name="Alpha", slug="alpha"))
    await db_session.commit()

    result = await db_session.execute(select(Project).where(Project.slug == "alpha"))
    fetched = result.scalar_one()
    assert fetched.name == "Alpha"
