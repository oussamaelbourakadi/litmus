"""Dataset endpoints: create a dataset with test cases, read it back."""

from __future__ import annotations

import csv
import io
import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.models.dataset import Dataset
from app.models.project import Project
from app.models.test_case import TestCase
from app.schemas.dataset import (
    CasesAppend,
    CsvUpload,
    DatasetCreate,
    DatasetRead,
    DatasetSummary,
    TestCaseRead,
)

router = APIRouter(tags=["datasets"])


async def _require_dataset(db: AsyncSession, dataset_id: uuid.UUID) -> Dataset:
    dataset = await db.get(Dataset, dataset_id)
    if dataset is None or dataset.is_deleted:
        raise HTTPException(status_code=404, detail="dataset not found")
    return dataset


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


@router.get("/projects/{project_id}/datasets", response_model=list[DatasetSummary])
async def list_datasets(project_id: uuid.UUID, db: DbSession) -> list[Dataset]:
    result = await db.execute(
        select(Dataset).where(Dataset.project_id == project_id, Dataset.is_deleted.is_(False))
    )
    return list(result.scalars().all())


@router.post(
    "/datasets/{dataset_id}/cases",
    response_model=DatasetRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_cases(dataset_id: uuid.UUID, payload: CasesAppend, db: DbSession) -> DatasetRead:
    await _require_dataset(db, dataset_id)
    for case in payload.cases:
        db.add(
            TestCase(
                dataset_id=dataset_id,
                input=case.input,
                expected=case.expected,
                case_metadata=case.metadata,
            )
        )
    await db.commit()
    return await _read_dataset(db, dataset_id)


@router.post(
    "/datasets/{dataset_id}/cases/csv",
    response_model=DatasetRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_cases_csv(dataset_id: uuid.UUID, payload: CsvUpload, db: DbSession) -> DatasetRead:
    await _require_dataset(db, dataset_id)
    reader = csv.DictReader(io.StringIO(payload.csv))
    if reader.fieldnames is None or "input" not in reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV must have an 'input' column")

    added = 0
    for row in reader:
        text = (row.get("input") or "").strip()
        if not text:
            continue
        expected = row.get("expected")
        db.add(
            TestCase(
                dataset_id=dataset_id,
                input=text,
                expected=expected.strip() if expected else None,
            )
        )
        added += 1
    if added == 0:
        raise HTTPException(status_code=400, detail="CSV contained no usable rows")
    await db.commit()
    return await _read_dataset(db, dataset_id)
