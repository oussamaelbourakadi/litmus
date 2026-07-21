"""End-to-end API tests: project -> dataset -> run (async) -> results."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from httpx import AsyncClient

WaitForRun = Callable[[AsyncClient, str], Awaitable[dict[str, Any]]]


async def _make_project_and_dataset(client: AsyncClient, cases: list[dict[str, str]]) -> str:
    project = await client.post("/projects", json={"name": "P", "slug": "p"})
    assert project.status_code == 201
    project_id = project.json()["id"]

    dataset = await client.post(
        f"/projects/{project_id}/datasets",
        json={"name": "D", "cases": cases},
    )
    assert dataset.status_code == 201
    dataset_id: str = dataset.json()["id"]
    return dataset_id


async def test_run_is_created_pending_then_completes(
    api_client: AsyncClient, wait_for_run: WaitForRun
) -> None:
    dataset_id = await _make_project_and_dataset(
        api_client, [{"input": "ping", "expected": "x"}, {"input": "pong", "expected": "y"}]
    )

    # The mock output always contains "mock", so a regex on "mock" passes for all cases.
    response = await api_client.post(
        f"/datasets/{dataset_id}/runs",
        json={
            "provider": "mock",
            "model": "mock",
            "evaluators": [{"name": "regex_match", "params": {"pattern": "mock"}}],
        },
    )
    assert response.status_code == 201
    created = response.json()
    assert created["status"] in {"pending", "running", "completed"}
    assert created["total_cases"] == 2

    final = await wait_for_run(api_client, created["id"])
    assert final["status"] == "completed"
    assert final["completed_cases"] == 2
    assert final["aggregates"]["total"] == 2
    assert final["aggregates"]["success_rate"] == 1.0
    assert "success_rate_ci" in final["aggregates"]
    assert len(final["results"]) == 2


async def test_run_with_repeats(api_client: AsyncClient, wait_for_run: WaitForRun) -> None:
    dataset_id = await _make_project_and_dataset(api_client, [{"input": "ping", "expected": "x"}])
    response = await api_client.post(
        f"/datasets/{dataset_id}/runs",
        json={"provider": "mock", "repeats": 3, "evaluators": [{"name": "exact_match"}]},
    )
    assert response.status_code == 201
    final = await wait_for_run(api_client, response.json()["id"])
    assert final["status"] == "completed"
    assert len(final["results"]) == 3
    assert final["aggregates"]["repeat_success_mean"] is not None


async def test_run_rejects_empty_dataset(api_client: AsyncClient) -> None:
    dataset_id = await _make_project_and_dataset(api_client, [])
    response = await api_client.post(f"/datasets/{dataset_id}/runs", json={})
    assert response.status_code == 400


async def test_run_rejects_bad_evaluator_spec(api_client: AsyncClient) -> None:
    dataset_id = await _make_project_and_dataset(api_client, [{"input": "a", "expected": "b"}])
    response = await api_client.post(
        f"/datasets/{dataset_id}/runs",
        json={"evaluators": [{"name": "regex_match", "params": {}}]},
    )
    assert response.status_code == 400


async def test_get_missing_run_is_404(api_client: AsyncClient) -> None:
    response = await api_client.get("/runs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
