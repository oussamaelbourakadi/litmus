"""Background run execution: status, progress, cancellation."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from httpx import AsyncClient

WaitForRun = Callable[[AsyncClient, str], Awaitable[dict[str, Any]]]

_MISSING = "00000000-0000-0000-0000-000000000000"


async def _dataset(client: AsyncClient, cases: list[dict[str, str]]) -> str:
    project_id = (await client.post("/projects", json={"name": "P", "slug": "p"})).json()["id"]
    dataset = await client.post(
        f"/projects/{project_id}/datasets", json={"name": "D", "cases": cases}
    )
    return str(dataset.json()["id"])


async def test_status_endpoint_reports_progress(
    api_client: AsyncClient, wait_for_run: WaitForRun
) -> None:
    dataset_id = await _dataset(
        api_client, [{"input": "a", "expected": "b"}, {"input": "c", "expected": "d"}]
    )
    run = (
        await api_client.post(
            f"/datasets/{dataset_id}/runs",
            json={"provider": "mock", "evaluators": [{"name": "exact_match"}]},
        )
    ).json()

    status = (await api_client.get(f"/runs/{run['id']}/status")).json()
    assert status["total_cases"] == 2
    assert status["status"] in {"pending", "running", "completed"}

    await wait_for_run(api_client, run["id"])
    done = (await api_client.get(f"/runs/{run['id']}/status")).json()
    assert done["status"] == "completed"
    assert done["completed_cases"] == 2


async def test_cancel_endpoint(api_client: AsyncClient, wait_for_run: WaitForRun) -> None:
    dataset_id = await _dataset(api_client, [{"input": "a", "expected": "b"}])
    run = (
        await api_client.post(
            f"/datasets/{dataset_id}/runs",
            json={
                "provider": "scripted",
                "model": "mock-large",
                "evaluators": [{"name": "exact_match"}],
            },
        )
    ).json()

    cancel = await api_client.post(f"/runs/{run['id']}/cancel")
    assert cancel.status_code == 200

    final = await wait_for_run(api_client, run["id"])
    # Mock runs are fast, so it may finish before the cancel takes effect.
    assert final["status"] in {"cancelled", "completed"}


async def test_cancel_missing_run_is_404(api_client: AsyncClient) -> None:
    response = await api_client.post(f"/runs/{_MISSING}/cancel")
    assert response.status_code == 404


async def test_status_missing_run_is_404(api_client: AsyncClient) -> None:
    response = await api_client.get(f"/runs/{_MISSING}/status")
    assert response.status_code == 404


async def test_scripted_run_produces_real_metrics(
    api_client: AsyncClient, wait_for_run: WaitForRun
) -> None:
    cases = [
        {"input": "What is the capital of France?", "expected": "Paris"},
        {"input": "What is 2 + 2?", "expected": "4"},
    ]
    dataset_id = await _dataset(api_client, cases)
    run = (
        await api_client.post(
            f"/datasets/{dataset_id}/runs",
            json={
                "provider": "scripted",
                "model": "mock-large",
                "evaluators": [{"name": "exact_match"}],
            },
        )
    ).json()

    final = await wait_for_run(api_client, run["id"])
    assert final["status"] == "completed"
    assert final["aggregates"]["success_rate"] == 1.0
    assert final["aggregates"]["latency_p50"] > 0  # the scripted provider simulates latency
