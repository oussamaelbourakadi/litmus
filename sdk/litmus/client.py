"""Thin HTTP client for a running Litmus server (optional)."""

from __future__ import annotations

from types import TracebackType
from typing import Any

import httpx


class LitmusClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        *,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"), timeout=timeout, transport=transport
        )

    def __enter__(self) -> LitmusClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def _json(self, response: httpx.Response) -> dict[str, Any]:
        response.raise_for_status()
        data: Any = response.json()
        return data if isinstance(data, dict) else {"data": data}

    def health(self) -> dict[str, Any]:
        return self._json(self._client.get("/health"))

    def create_project(self, name: str, slug: str) -> dict[str, Any]:
        return self._json(self._client.post("/projects", json={"name": name, "slug": slug}))

    def create_dataset(
        self, project_id: str, name: str, cases: list[dict[str, Any]]
    ) -> dict[str, Any]:
        return self._json(
            self._client.post(
                f"/projects/{project_id}/datasets", json={"name": name, "cases": cases}
            )
        )

    def run(
        self,
        dataset_id: str,
        *,
        provider: str = "mock",
        evaluators: list[dict[str, Any]] | None = None,
        repeats: int = 1,
    ) -> dict[str, Any]:
        body = {
            "provider": provider,
            "repeats": repeats,
            "evaluators": evaluators or [{"name": "exact_match"}],
        }
        return self._json(self._client.post(f"/datasets/{dataset_id}/runs", json=body))

    def compare(self, base_run_id: str, candidate_run_id: str) -> dict[str, Any]:
        return self._json(
            self._client.post(
                "/compare",
                json={"base_run_id": base_run_id, "candidate_run_id": candidate_run_id},
            )
        )
