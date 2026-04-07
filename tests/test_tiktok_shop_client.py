from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
from unittest.mock import AsyncMock

import httpx
import pytest

from ingestion.auth import TikTokOAuth
from ingestion.clients import TikTokShopAuthError, TikTokShopClient


def _oauth() -> TikTokOAuth:
    return TikTokOAuth("app-key", "app-secret")


def test_search_products_returns_list(monkeypatch: pytest.MonkeyPatch) -> None:
    oauth = _oauth()
    client = TikTokShopClient(oauth)
    monkeypatch.setattr(oauth, "get_valid_token", AsyncMock(return_value="access-token"))

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/affiliate/product/search"
        assert request.headers["access-token"] == "access-token"
        return httpx.Response(200, json={"data": {"products": [{"product_id": "product-1"}]}})

    monkeypatch.setattr(
        client,
        "_build_client",
        lambda: httpx.AsyncClient(
            transport=httpx.MockTransport(handler),
            base_url=client.BASE_URL,
        ),
    )

    products = asyncio.run(client.search_products("led strip"))

    assert products == [{"product_id": "product-1"}]


def test_request_signing_includes_required_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TikTokShopClient(_oauth())
    monkeypatch.setattr(client, "_current_timestamp", lambda: 1_710_000_000)

    signed = client._sign_request("/api/affiliate/product/detail", {"product_id": "123"}, {})

    assert signed["app_key"] == "app-key"
    assert signed["timestamp"] == 1_710_000_000
    assert "sign" in signed


def test_sign_is_hmac_sha256_of_correct_string(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TikTokShopClient(_oauth())
    monkeypatch.setattr(client, "_current_timestamp", lambda: 1_710_000_000)

    signed = client._sign_request("/api/affiliate/product/detail", {"product_id": "123"}, {})

    expected = hmac.new(
        b"app-secret",
        (b"app-secret/api/affiliate/product/detailapp_keyapp-keyproduct_id1231710000000"),
        hashlib.sha256,
    ).hexdigest()

    assert signed["sign"] == expected


def test_sign_includes_body_fields_for_post_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TikTokShopClient(_oauth())
    monkeypatch.setattr(client, "_current_timestamp", lambda: 1_710_000_000)

    signed = client._sign_request(
        "/api/affiliate/product/search",
        {},
        {
            "keyword": "led strip",
            "filters": {"region": "BR"},
            "page_size": 100,
        },
    )

    expected = hmac.new(
        b"app-secret",
        (
            b"app-secret"
            b"/api/affiliate/product/search"
            b"app_keyapp-key"
            b"filtersregionBRkeywordled strippage_size100"
            b"1710000000"
        ),
        hashlib.sha256,
    ).hexdigest()

    assert signed["sign"] == expected


def test_get_hot_products_passes_region_br(monkeypatch: pytest.MonkeyPatch) -> None:
    oauth = _oauth()
    client = TikTokShopClient(oauth)
    monkeypatch.setattr(oauth, "get_valid_token", AsyncMock(return_value="access-token"))
    observed: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        observed["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"data": {"products": []}})

    monkeypatch.setattr(
        client,
        "_build_client",
        lambda: httpx.AsyncClient(
            transport=httpx.MockTransport(handler),
            base_url=client.BASE_URL,
        ),
    )

    asyncio.run(client.get_hot_products())

    body = observed["body"]
    assert isinstance(body, dict)
    assert body["filters"]["region"] == "BR"


def test_client_raises_on_401(monkeypatch: pytest.MonkeyPatch) -> None:
    oauth = _oauth()
    client = TikTokShopClient(oauth)
    monkeypatch.setattr(oauth, "get_valid_token", AsyncMock(return_value="access-token"))
    monkeypatch.setattr(
        client,
        "_build_client",
        lambda: httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(401, json={})),
            base_url=client.BASE_URL,
        ),
    )

    with pytest.raises(TikTokShopAuthError, match="token expired"):
        asyncio.run(client.search_products("led strip"))
