"""Dataset endpoints: create a dataset with test cases, read it back."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.models.dataset import Dataset
from app.models.project import Project
from app.models.test_case import TestCase
from app.schemas.dataset import DatasetCreate, DatasetRead, TestCaseRead

router = APIRouter(tags=["datasets"])


async def _read_dataset(db: AsyncSession, dataset_id: uuid.UUID) -> DatasetRead:
    dataset = await db.get(Dataset, dataset_id)
    if dataset is None or dataset.is_deleted:
        raise HTTPException(status_code=404, detail="dataset not found")
    result = await db.execute(select(TestCase).where(TestCase.dataset_id == dataset_id))
    cases = [
        TestCaseRead(id=tc.id, input=tc.input, expected=tc.expected, metadata=tc.case_metadata)
        for tc in result.scalars().all()
    ]
    return DatasetRead(
        id=dataset.id,
        project_id=dataset.project_id,
        name=dataset.name,
        description=dataset.description,
        cases=cases,
    )


@router.post(
    "/projects/{project_id}/datasets",
    response_model=DatasetRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_dataset(
    project_id: uuid.UUID, payload: DatasetCreate, db: DbSession
) -> DatasetRead:
    project = await db.get(Project, project_id)
    if project is None or project.is_deleted:
        raise HTTPException(status_code=404, detail="project not found")

    dataset = Dataset(project_id=project_id, name=payload.name, description=payload.description)
    db.add(dataset)
    await db.flush()
    for case in payload.cases:
        db.add(
            TestCase(
                dataset_id=dataset.id,
                input=case.input,
                expected=case.expected,
                case_metadata=case.metadata,
            )
        )
    await db.commit()
    return await _read_dataset(db, dataset.id)


@router.get("/datasets/{dataset_id}", response_model=DatasetRead)
async def get_dataset(dataset_id: uuid.UUID, db: DbSession) -> DatasetRead:
    return await _read_dataset(db, dataset_id)
