from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from apps.api.main import create_app
from ingestion.auth import TikTokOAuth, TokenCache, TokenData
from services.shared.config import ROOT_DIR, AppSettings


def _build_client() -> TestClient:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    db_path = temp_dir / f"api-tiktok-auth-{uuid4().hex}.sqlite3"
    settings = AppSettings(database_url=f"sqlite+pysqlite:///{db_path.as_posix()}")
    return TestClient(create_app(settings))


def _token() -> TokenData:
    now = datetime.now(UTC)
    return TokenData(
        access_token="access-token",
        refresh_token="refresh-token",
        expires_at=now + timedelta(hours=1),
        refresh_expires_at=now + timedelta(days=1),
    )


def _cache_file() -> Path:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    return temp_dir / f"tiktok-token-{uuid4().hex}.json"


def test_tiktok_callback_persists_token_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cache_file = _cache_file()
    monkeypatch.setenv("TIKTOK_APP_KEY", "app-key")
    monkeypatch.setenv("TIKTOK_APP_SECRET", "app-secret")
    monkeypatch.setenv("TIKTOK_OAUTH_STATE", "local-state")
    monkeypatch.setenv("TIKTOK_TOKEN_CACHE_FILE", str(cache_file))

    async def fake_get_access_token(self: TikTokOAuth, auth_code: str) -> TokenData:
        assert auth_code == "oauth-code"
        return _token()

    monkeypatch.setattr(TikTokOAuth, "get_access_token", fake_get_access_token)

    client = _build_client()
    response = client.get(
        "/auth/tiktok/callback",
        params={"code": "oauth-code", "state": "local-state"},
    )

    assert response.status_code == 200
    assert "Autenticacao concluida" in response.text
    cached_token = TokenCache(cache_file).load()
    assert cached_token is not None
    assert cached_token.access_token == "access-token"


def test_tiktok_callback_requires_authorization_code() -> None:
    client = _build_client()

    response = client.get("/auth/tiktok/callback")

    assert response.status_code == 400
    assert "Codigo de autorizacao ausente" in response.text


def test_tiktok_callback_rejects_missing_or_invalid_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TIKTOK_APP_KEY", "app-key")
    monkeypatch.setenv("TIKTOK_APP_SECRET", "app-secret")
    monkeypatch.setenv("TIKTOK_OAUTH_STATE", "local-state")

    client = _build_client()

    missing_state = client.get("/auth/tiktok/callback", params={"code": "oauth-code"})
    invalid_state = client.get(
        "/auth/tiktok/callback",
        params={"code": "oauth-code", "state": "wrong-state"},
    )

    assert missing_state.status_code == 400
    assert "State invalido" in missing_state.text
    assert invalid_state.status_code == 400
    assert "State invalido" in invalid_state.text
