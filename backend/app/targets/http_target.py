"""HttpTarget — evaluate an external AI endpoint over HTTP."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from time import perf_counter

import httpx

from app.config import get_settings
from app.providers._http import PooledHttpClient
from app.targets.base import Target, TargetResponse, target_registry


class HttpTargetError(RuntimeError):
    """Raised when the HTTP response does not contain the expected output field."""


@target_registry.register("http")
class HttpTarget(Target):
    """POST the input to a URL and extract the output from the JSON response.

    ``output_path`` is a sequence of keys traversed into the response JSON, e.g.
    ``("data", "text")`` reads ``response["data"]["text"]``.
    """

    name = "http"

    def __init__(
        self,
        url: str,
        *,
        method: str = "POST",
        input_field: str = "input",
        output_path: Sequence[str] = ("output",),
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._url = url
        self._method = method.upper()
        self._input_field = input_field
        self._output_path = tuple(output_path)
        self._headers = dict(headers) if headers else None
        self._http = PooledHttpClient(
            timeout=timeout or get_settings().request_timeout, transport=transport
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def run(self, input: str) -> TargetResponse:
        start = perf_counter()
        response = await self._http.get().request(
            self._method,
            self._url,
            json={self._input_field: input},
            headers=self._headers,
        )
        response.raise_for_status()
        data = response.json()
        latency_ms = (perf_counter() - start) * 1000

        return TargetResponse(
            output=self._extract(data),
            latency_ms=latency_ms,
            metadata={"status_code": response.status_code},
        )

    def _extract(self, data: object) -> str:
        current = data
        for key in self._output_path:
            if not isinstance(current, Mapping) or key not in current:
                raise HttpTargetError(f"output path {self._output_path} not found in response")
            current = current[key]
        return str(current)
