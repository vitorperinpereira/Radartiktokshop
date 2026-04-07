"""TikTok Shop OAuth client and token lifecycle helpers."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from ingestion.auth.token_cache import TokenCache

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class TokenData:
    """Normalized TikTok Shop OAuth token payload."""

    access_token: str
    refresh_token: str
    expires_at: datetime
    refresh_expires_at: datetime


class TikTokOAuth:
    """Manage TikTok Shop access tokens, refresh flow, and on-disk cache usage."""

    BASE_URL = "https://open-api.tiktokshop.com"

    def __init__(
        self,
        app_key: str,
        app_secret: str,
        *,
        auth_code: str | None = None,
        token_cache: TokenCache | None = None,
        timeout: float = 30.0,
    ) -> None:
        from ingestion.auth.token_cache import TokenCache

        self.app_key = app_key
        self.app_secret = app_secret
        self.auth_code = (auth_code or "").strip()
        self.token_cache = token_cache if token_cache is not None else TokenCache()
        self.timeout = timeout

    def _build_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.BASE_URL, timeout=self.timeout)

    @staticmethod
    def _parse_token_payload(payload: dict[str, Any]) -> TokenData:
        data = payload.get("data")
        if not isinstance(data, dict):
            raise RuntimeError("TikTok Shop OAuth response is missing the `data` object.")

        now = datetime.now(UTC)
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        access_expire_in = data.get("access_token_expire_in")
        refresh_expire_in = data.get("refresh_token_expire_in")
        if not isinstance(access_token, str) or not isinstance(refresh_token, str):
            raise RuntimeError("TikTok Shop OAuth response is missing token values.")
        if not isinstance(access_expire_in, int) or not isinstance(refresh_expire_in, int):
            raise RuntimeError("TikTok Shop OAuth response is missing token expirations.")

        return TokenData(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=now + timedelta(seconds=access_expire_in),
            refresh_expires_at=now + timedelta(seconds=refresh_expire_in),
        )

    async def _request_token(self, path: str, payload: dict[str, str]) -> TokenData:
        async with self._build_client() as client:
            response = await client.post(path, data=payload)

        if response.status_code >= 400:
            raise RuntimeError(
                f"TikTok Shop OAuth request failed with status `{response.status_code}`."
            )

        response_payload = response.json()
        if not isinstance(response_payload, dict):
            raise RuntimeError("TikTok Shop OAuth response is invalid.")
        return self._parse_token_payload(response_payload)

    async def get_access_token(self, auth_code: str) -> TokenData:
        """Exchange an authorization code for a fresh access token."""

        return await self._request_token(
            "/api/token/getAccessToken",
            {
                "app_key": self.app_key,
                "app_secret": self.app_secret,
                "auth_code": auth_code,
                "grant_type": "authorized_code",
            },
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenData:
        """Refresh an expired access token using the refresh token."""

        return await self._request_token(
            "/api/token/refreshToken",
            {
                "app_key": self.app_key,
                "app_secret": self.app_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )

    async def get_valid_token(self) -> str:
        """Return a valid TikTok Shop access token, refreshing or bootstrapping as needed."""

        cached_token = self.token_cache.load()
        if cached_token is not None and self.token_cache.is_valid(cached_token):
            return cached_token.access_token

        if cached_token is not None and self.token_cache.needs_refresh(cached_token):
            refreshed_token = await self.refresh_access_token(cached_token.refresh_token)
            self.token_cache.save(refreshed_token)
            return refreshed_token.access_token

        if self.auth_code:
            new_token = await self.get_access_token(self.auth_code)
            self.token_cache.save(new_token)
            return new_token.access_token

        logger.error("TikTok Shop API token expired - run: python -m ingestion.auth")
        raise RuntimeError("TikTok Shop API token expired - run: python -m ingestion.auth")
