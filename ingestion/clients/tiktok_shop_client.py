"""Async client for the TikTok Shop Partner API."""

from __future__ import annotations

import hashlib
import hmac
import time
from collections.abc import Mapping
from typing import Any, cast

import httpx

from ingestion.auth import TikTokOAuth

QueryPrimitive = str | int | float | bool | None


class TikTokShopAPIError(RuntimeError):
    """Raised when the TikTok Shop API returns a non-auth failure."""


class TikTokShopAuthError(TikTokShopAPIError):
    """Raised when the TikTok Shop API rejects the current access token."""


class TikTokShopClient:
    """Signed async client for the TikTok Shop Partner API."""

    BASE_URL = "https://open-api.tiktokshop.com"

    def __init__(
        self,
        oauth: TikTokOAuth,
        *,
        region: str = "BR",
        timeout: float = 30.0,
    ) -> None:
        self.oauth = oauth
        self.region = region
        self.timeout = timeout

    def _build_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.BASE_URL, timeout=self.timeout)

    @staticmethod
    def _canonical_params(params: Mapping[str, QueryPrimitive]) -> str:
        parts: list[str] = []
        for key in sorted(params):
            if key in {"sign", "timestamp"}:
                continue
            value = params[key]
            if value is None:
                continue
            parts.append(f"{key}{value}")
        return "".join(parts)

    @classmethod
    def _canonical_object(cls, value: object) -> str:
        if isinstance(value, Mapping):
            parts: list[str] = []
            for key in sorted(value):
                parts.append(f"{key}{cls._canonical_object(value[key])}")
            return "".join(parts)
        if isinstance(value, list):
            return "".join(cls._canonical_object(item) for item in value)
        if value is None:
            return ""
        return str(value)

    def _current_timestamp(self) -> int:
        return int(time.time())

    def _sign_request(
        self,
        path: str,
        params: dict[str, object],
        body: dict[str, object],
    ) -> dict[str, QueryPrimitive]:
        """Return query params enriched with `app_key`, `timestamp`, and `sign`."""

        signed_params: dict[str, QueryPrimitive] = {}
        for key, value in params.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                signed_params[key] = value
            else:
                signed_params[key] = str(value)
        signed_params["app_key"] = self.oauth.app_key
        timestamp = self._current_timestamp()
        canonical_params = self._canonical_params(signed_params)
        canonical_body = self._canonical_object(body)
        message = (
            f"{self.oauth.app_secret}{path}{canonical_params}{canonical_body}{timestamp}".encode()
        )
        signature = hmac.new(
            self.oauth.app_secret.encode("utf-8"),
            message,
            hashlib.sha256,
        ).hexdigest()
        signed_params["timestamp"] = timestamp
        signed_params["sign"] = signature
        return signed_params

    @staticmethod
    def _extract_data(payload: dict[str, Any]) -> dict[str, Any]:
        data = payload.get("data")
        if not isinstance(data, dict):
            raise TikTokShopAPIError("TikTok Shop API response is missing the `data` object.")
        return data

    @staticmethod
    def _extract_list(data: dict[str, Any]) -> list[dict[str, Any]]:
        for key in ("products", "product_list", "items", "list"):
            value = data.get(key)
            if isinstance(value, list):
                return [dict(item) for item in value if isinstance(item, dict)]
        return []

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, object] | None = None,
        json_body: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        request_params = self._sign_request(path, params or {}, json_body or {})
        access_token = await self.oauth.get_valid_token()

        async with self._build_client() as client:
            response = await client.request(
                method,
                path,
                params=cast(httpx._types.QueryParamTypes | None, request_params),
                json=json_body,
                headers={"access-token": access_token},
            )

        if response.status_code == 401:
            raise TikTokShopAuthError(
                "TikTok Shop API token expired - run: python -m ingestion.auth"
            )
        if response.status_code >= 400:
            raise TikTokShopAPIError(
                f"TikTok Shop API request failed with status `{response.status_code}`."
            )

        payload = response.json()
        if not isinstance(payload, dict):
            raise TikTokShopAPIError("TikTok Shop API response is invalid.")
        return self._extract_data(payload)

    async def search_products(
        self,
        keyword: str,
        page_size: int = 100,
        sort_by: str = "SALES_VOLUME",
    ) -> list[dict[str, Any]]:
        """Search TikTok Shop affiliate products for one keyword."""

        data = await self._request(
            "POST",
            "/api/affiliate/product/search",
            json_body={
                "keyword": keyword,
                "page_size": page_size,
                "sort_by": sort_by,
                "filters": {"region": self.region},
            },
        )
        return self._extract_list(data)

    async def get_product_detail(self, product_id: str) -> dict[str, Any]:
        """Fetch the full TikTok Shop affiliate product detail payload."""

        data = await self._request(
            "GET",
            "/api/affiliate/product/detail",
            params={"product_id": product_id},
        )
        product = data.get("product")
        if isinstance(product, dict):
            return dict(product)
        return data

    async def get_hot_products(
        self,
        category_id: str | None = None,
        page_size: int = 50,
    ) -> list[dict[str, Any]]:
        """Fetch TikTok Shop hot products for the configured region."""

        filters: dict[str, object] = {"region": self.region}
        if category_id is not None:
            filters["category_id"] = category_id

        data = await self._request(
            "POST",
            "/api/affiliate/product/hotProduct/search",
            json_body={
                "page_size": page_size,
                "sort_by": "SALES_VOLUME",
                "filters": filters,
            },
        )
        return self._extract_list(data)
