from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import pytest

from ingestion.auth import TikTokAuthSettings, TikTokOAuth, TokenCache, TokenData
from services.shared.config import ROOT_DIR


def _token(
    *,
    access_token: str = "access-token",
    refresh_token: str = "refresh-token",
    access_delta: timedelta = timedelta(hours=1),
    refresh_delta: timedelta = timedelta(days=1),
) -> TokenData:
    now = datetime.now(UTC)
    return TokenData(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=now + access_delta,
        refresh_expires_at=now + refresh_delta,
    )


def _workspace_tmp_path(prefix: str) -> Path:
    base_dir = ROOT_DIR / ".tmp"
    base_dir.mkdir(parents=True, exist_ok=True)
    target_dir = base_dir / f"{prefix}-{uuid4().hex}"
    target_dir.mkdir()
    return target_dir / "tiktok_token.json"


def test_get_access_token_returns_token_data(monkeypatch: pytest.MonkeyPatch) -> None:
    oauth = TikTokOAuth("app-key", "app-secret")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": {
                    "access_token": "access-1",
                    "refresh_token": "refresh-1",
                    "access_token_expire_in": 3600,
                    "refresh_token_expire_in": 86400,
                }
            },
        )

    monkeypatch.setattr(
        oauth,
        "_build_client",
        lambda: httpx.AsyncClient(
            transport=httpx.MockTransport(handler),
            base_url=oauth.BASE_URL,
        ),
    )

    token = asyncio.run(oauth.get_access_token("auth-code"))

    assert token.access_token == "access-1"
    assert token.refresh_token == "refresh-1"
    assert token.expires_at > datetime.now(UTC)


def test_refresh_token_called_when_expired(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cache = TokenCache(_workspace_tmp_path("oauth-refresh"))
    cache.save(
        _token(
            access_token="expired-access",
            refresh_token="refresh-1",
            access_delta=timedelta(minutes=-1),
            refresh_delta=timedelta(hours=2),
        )
    )
    oauth = TikTokOAuth("app-key", "app-secret", token_cache=cache)
    refresh_mock = AsyncMock(return_value=_token(access_token="fresh-access"))
    monkeypatch.setattr(oauth, "refresh_access_token", refresh_mock)

    token = asyncio.run(oauth.get_valid_token())

    assert token == "fresh-access"
    assert refresh_mock.await_count == 1
    loaded = cache.load()
    assert loaded is not None
    assert loaded.access_token == "fresh-access"


def test_get_valid_token_uses_cache_if_fresh(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cache = TokenCache(_workspace_tmp_path("oauth-cache"))
    cache.save(_token(access_token="cached-access"))
    oauth = TikTokOAuth("app-key", "app-secret", token_cache=cache)
    refresh_mock = AsyncMock()
    monkeypatch.setattr(oauth, "refresh_access_token", refresh_mock)

    token = asyncio.run(oauth.get_valid_token())

    assert token == "cached-access"
    assert refresh_mock.await_count == 0


def test_token_cache_save_and_load_roundtrip() -> None:
    cache = TokenCache(_workspace_tmp_path("oauth-roundtrip"))
    token = _token()

    cache.save(token)
    loaded = cache.load()

    assert loaded == token


def test_needs_refresh_when_access_expired_but_refresh_valid() -> None:
    token = _token(
        access_delta=timedelta(minutes=-5),
        refresh_delta=timedelta(hours=3),
    )

    assert TokenCache.needs_refresh(token) is True


def test_tiktok_auth_settings_load_without_apify_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cache_file = _workspace_tmp_path("oauth-settings")
    monkeypatch.delenv("APIFY_TOKEN", raising=False)
    monkeypatch.setenv("TIKTOK_APP_KEY", "app-key")
    monkeypatch.setenv("TIKTOK_APP_SECRET", "app-secret")
    monkeypatch.setenv("TIKTOK_AUTH_CODE", "stored-auth-code")
    monkeypatch.setenv("TIKTOK_OAUTH_STATE", "local-oauth-state")
    monkeypatch.setenv("TIKTOK_TOKEN_CACHE_FILE", str(cache_file))

    settings = TikTokAuthSettings.from_env()

    assert settings.app_key == "app-key"
    assert settings.app_secret == "app-secret"
    assert settings.auth_code == "stored-auth-code"
    assert settings.oauth_state == "local-oauth-state"
    assert settings.token_cache_file == cache_file
