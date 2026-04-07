"""Persistent cache for TikTok Shop OAuth tokens."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from ingestion.auth.tiktok_oauth import TokenData


class TokenCache:
    """Serialize and validate TikTok Shop OAuth tokens on disk."""

    CACHE_FILE = ".cache/auth/tiktok_token.json"

    def __init__(self, cache_file: str | Path | None = None) -> None:
        self.cache_file = Path(cache_file or self.CACHE_FILE)

    def save(self, token: TokenData) -> None:
        """Persist one token payload to the configured cache file."""

        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "access_token": token.access_token,
            "refresh_token": token.refresh_token,
            "expires_at": token.expires_at.isoformat(),
            "refresh_expires_at": token.refresh_expires_at.isoformat(),
        }
        self.cache_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self) -> TokenData | None:
        """Load one token payload from disk, returning `None` on missing/corrupt data."""

        if not self.cache_file.exists():
            return None

        try:
            payload = json.loads(self.cache_file.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                return None
            return TokenData(
                access_token=str(payload["access_token"]),
                refresh_token=str(payload["refresh_token"]),
                expires_at=datetime.fromisoformat(str(payload["expires_at"])).astimezone(UTC),
                refresh_expires_at=datetime.fromisoformat(
                    str(payload["refresh_expires_at"])
                ).astimezone(UTC),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return None

    @staticmethod
    def is_valid(token: TokenData) -> bool:
        """Return `True` when the access token remains valid for at least 5 minutes."""

        return token.expires_at > datetime.now(UTC) + timedelta(minutes=5)

    @staticmethod
    def needs_refresh(token: TokenData) -> bool:
        """Return `True` when the access token expired but the refresh token still works."""

        now = datetime.now(UTC)
        return token.expires_at <= now < token.refresh_expires_at
