"""Async Apify client with retry-aware actor orchestration helpers."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import Any

import httpx

PrimitiveQueryValue = str | int | float | bool | None
QueryParamValue = PrimitiveQueryValue | list[PrimitiveQueryValue]


class ApifyClient:
    """Thin async client for the specific Apify actor flow used by the ingestion layer."""

    BASE_URL = "https://api.apify.com/v2"
    MAX_RETRIES = 3

    def __init__(self, token: str, poll_interval: int = 5, timeout: int = 120) -> None:
        self._token = token
        self.poll_interval = poll_interval
        self.timeout = timeout

    def _build_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        )

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, QueryParamValue] | None = None,
        json_body: Mapping[str, object] | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        delay_seconds = 1.0
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                async with self._build_client() as client:
                    response = await client.request(method, path, params=params, json=json_body)
            except httpx.TimeoutException as exc:
                if attempt == self.MAX_RETRIES:
                    raise RuntimeError("Apify request timed out.") from exc
                await asyncio.sleep(delay_seconds)
                delay_seconds *= 2.0
                continue
            except httpx.RequestError as exc:
                raise RuntimeError("Apify request failed due to a network error.") from exc

            if response.status_code >= 500:
                if attempt == self.MAX_RETRIES:
                    raise RuntimeError(
                        f"Apify request failed with server error `{response.status_code}`."
                    )
                await asyncio.sleep(delay_seconds)
                delay_seconds *= 2.0
                continue

            if response.status_code >= 400:
                raise RuntimeError(
                    f"Apify request failed with status `{response.status_code}`."
                )

            payload = response.json()
            if isinstance(payload, dict):
                return payload
            if isinstance(payload, list):
                return [dict(item) for item in payload if isinstance(item, dict)]
            raise RuntimeError("Apify response body is not JSON-serializable.")

        raise RuntimeError("Apify request failed unexpectedly.")

    @staticmethod
    def _extract_data(payload: dict[str, Any]) -> dict[str, Any]:
        data = payload.get("data")
        if not isinstance(data, dict):
            raise RuntimeError("Apify response payload is missing the `data` object.")
        return data

    async def run_actor(self, actor_id: str, input_data: dict[str, object]) -> str:
        """Trigger one actor run and return the generated Apify run identifier."""

        payload = await self._request_json("POST", f"/acts/{actor_id}/runs", json_body=input_data)
        if not isinstance(payload, dict):
            raise RuntimeError("Apify actor run response is invalid.")
        data = self._extract_data(payload)
        run_id = data.get("id")
        if not isinstance(run_id, str) or not run_id:
            raise RuntimeError("Apify actor run response is missing a valid run id.")
        return run_id

    async def wait_for_run(self, run_id: str) -> dict[str, Any]:
        """Poll a run until it succeeds or fails with a terminal error."""

        start_time = asyncio.get_running_loop().time()
        while True:
            payload = await self._request_json("GET", f"/actor-runs/{run_id}")
            if not isinstance(payload, dict):
                raise RuntimeError("Apify actor run status response is invalid.")
            data = self._extract_data(payload)
            status = data.get("status")
            if status == "SUCCEEDED":
                return data
            if status in {"FAILED", "ABORTED", "TIMED-OUT"}:
                raise RuntimeError(f"Apify run `{run_id}` ended with status `{status}`.")
            if (asyncio.get_running_loop().time() - start_time) >= float(self.timeout):
                raise RuntimeError(f"Timed out while waiting for Apify run `{run_id}`.")
            await asyncio.sleep(float(self.poll_interval))

    async def get_dataset_items(self, dataset_id: str) -> list[dict[str, Any]]:
        """Fetch and return the raw JSON items for one Apify dataset."""

        payload = await self._request_json(
            "GET",
            f"/datasets/{dataset_id}/items",
            params={"format": "json"},
        )
        if not isinstance(payload, list):
            raise RuntimeError("Apify dataset response is invalid.")
        return [dict(item) for item in payload]

    async def run_and_collect(
        self, actor_id: str, input_data: dict[str, object]
    ) -> list[dict[str, Any]]:
        """Trigger an actor, wait for completion, and return the dataset items."""

        run_id = await self.run_actor(actor_id, input_data)
        metadata = await self.wait_for_run(run_id)
        dataset_id = metadata.get("defaultDatasetId")
        if not isinstance(dataset_id, str) or not dataset_id:
            raise RuntimeError(f"Apify run `{run_id}` did not expose a dataset id.")
        return await self.get_dataset_items(dataset_id)
