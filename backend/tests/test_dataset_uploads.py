"""Dataset listing, case append (JSON/CSV), and run listing."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from httpx import AsyncClient

WaitForRun = Callable[[AsyncClient, str], Awaitable[dict[str, Any]]]


async def _project(client: AsyncClient) -> str:
    return str((await client.post("/projects", json={"name": "P", "slug": "p"})).json()["id"])


async def _dataset(client: AsyncClient, project_id: str) -> str:
    response = await client.post(f"/projects/{project_id}/datasets", json={"name": "D"})
    return str(response.json()["id"])


async def test_list_datasets(api_client: AsyncClient) -> None:
    project_id = await _project(api_client)
    await api_client.post(f"/projects/{project_id}/datasets", json={"name": "D1"})
    await api_client.post(f"/projects/{project_id}/datasets", json={"name": "D2"})
    response = await api_client.get(f"/projects/{project_id}/datasets")
    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_append_cases_json(api_client: AsyncClient) -> None:
    project_id = await _project(api_client)
    dataset_id = await _dataset(api_client, project_id)
    response = await api_client.post(
        f"/datasets/{dataset_id}/cases", json={"cases": [{"input": "a", "expected": "b"}]}
    )
    assert response.status_code == 201
    assert len(response.json()["cases"]) == 1


async def test_upload_csv(api_client: AsyncClient) -> None:
    project_id = await _project(api_client)
    dataset_id = await _dataset(api_client, project_id)
    response = await api_client.post(
        f"/datasets/{dataset_id}/cases/csv",
        json={"csv": "input,expected\nping,pong\nfoo,bar\n"},
    )
    assert response.status_code == 201
    assert len(response.json()["cases"]) == 2


async def test_upload_csv_requires_input_column(api_client: AsyncClient) -> None:
    project_id = await _project(api_client)
    dataset_id = await _dataset(api_client, project_id)
    response = await api_client.post(
        f"/datasets/{dataset_id}/cases/csv", json={"csv": "foo,bar\n1,2\n"}
    )
    assert response.status_code == 400


async def test_list_runs(api_client: AsyncClient, wait_for_run: WaitForRun) -> None:
    project_id = await _project(api_client)
    dataset = await api_client.post(
        f"/projects/{project_id}/datasets",
        json={"name": "D", "cases": [{"input": "a", "expected": "b"}]},
    )
    dataset_id = dataset.json()["id"]
    run = await api_client.post(
        f"/datasets/{dataset_id}/runs", json={"evaluators": [{"name": "exact_match"}]}
    )
    await wait_for_run(api_client, run.json()["id"])

    response = await api_client.get(f"/datasets/{dataset_id}/runs")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["status"] == "completed"
