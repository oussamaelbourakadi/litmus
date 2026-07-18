"""End-to-end comparison API tests."""

from __future__ import annotations

from httpx import AsyncClient


async def _dataset(client: AsyncClient) -> str:
    project_id = (await client.post("/projects", json={"name": "P", "slug": "p"})).json()["id"]
    dataset = await client.post(
        f"/projects/{project_id}/datasets",
        json={"name": "D", "cases": [{"input": "ping", "expected": "nope"}]},
    )
    return str(dataset.json()["id"])


async def _run(client: AsyncClient, dataset_id: str, evaluators: list[dict[str, object]]) -> str:
    response = await client.post(f"/datasets/{dataset_id}/runs", json={"evaluators": evaluators})
    return str(response.json()["id"])


async def test_compare_detects_regression(api_client: AsyncClient) -> None:
    dataset_id = await _dataset(api_client)
    good = await _run(
        api_client, dataset_id, [{"name": "regex_match", "params": {"pattern": "mock"}}]
    )
    bad = await _run(api_client, dataset_id, [{"name": "exact_match"}])

    response = await api_client.post(
        "/compare", json={"base_run_id": good, "candidate_run_id": bad}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success_rate_base"] == 1.0
    assert body["success_rate_candidate"] == 0.0
    assert body["regressions"] >= 1
    assert body["verdict"]["passed"] is False


async def test_compare_no_regression(api_client: AsyncClient) -> None:
    dataset_id = await _dataset(api_client)
    evaluators = [{"name": "regex_match", "params": {"pattern": "mock"}}]
    base = await _run(api_client, dataset_id, evaluators)
    candidate = await _run(api_client, dataset_id, evaluators)

    response = await api_client.post(
        "/compare", json={"base_run_id": base, "candidate_run_id": candidate}
    )
    assert response.json()["verdict"]["passed"] is True


async def test_compare_missing_run_is_404(api_client: AsyncClient) -> None:
    dataset_id = await _dataset(api_client)
    base = await _run(api_client, dataset_id, [{"name": "exact_match"}])
    response = await api_client.post(
        "/compare",
        json={
            "base_run_id": base,
            "candidate_run_id": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert response.status_code == 404
