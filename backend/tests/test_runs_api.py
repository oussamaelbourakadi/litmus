"""End-to-end API tests: project -> dataset -> run -> results."""

from __future__ import annotations

from httpx import AsyncClient


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


async def test_run_persists_and_is_readable(api_client: AsyncClient) -> None:
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
    body = response.json()
    assert body["status"] == "completed"
    assert body["aggregates"]["total"] == 2
    assert body["aggregates"]["success_rate"] == 1.0
    assert "success_rate_ci" in body["aggregates"]
    assert len(body["results"]) == 2

    run_id = body["id"]
    fetched = await api_client.get(f"/runs/{run_id}")
    assert fetched.status_code == 200
    assert fetched.json()["aggregates"]["success_rate"] == 1.0


async def test_run_with_repeats(api_client: AsyncClient) -> None:
    dataset_id = await _make_project_and_dataset(api_client, [{"input": "ping", "expected": "x"}])
    response = await api_client.post(
        f"/datasets/{dataset_id}/runs",
        json={"provider": "mock", "repeats": 3, "evaluators": [{"name": "exact_match"}]},
    )
    assert response.status_code == 201
    body = response.json()
    assert len(body["results"]) == 3
    assert body["aggregates"]["repeat_success_mean"] is not None


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
