"""Environment-backed settings for TikTok Shop OAuth flows."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from ingestion.auth.tiktok_oauth import TikTokOAuth
from ingestion.auth.token_cache import TokenCache

ROOT_DIR = Path(__file__).resolve().parents[2]


def _resolve_cache_file(raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return ROOT_DIR / candidate


@dataclass(frozen=True, slots=True)
class TikTokAuthSettings:
    """Minimal settings required to exchange and cache TikTok Shop tokens."""

    app_key: str
    app_secret: str
    auth_code: str = ""
    oauth_state: str = ""
    token_cache_file: Path = ROOT_DIR / TokenCache.CACHE_FILE

    @classmethod
    def from_env(cls) -> TikTokAuthSettings:
        """Load the TikTok OAuth settings from `.env` and the process environment."""

        load_dotenv(ROOT_DIR / ".env")

        app_key = os.getenv("TIKTOK_APP_KEY", "").strip()
        app_secret = os.getenv("TIKTOK_APP_SECRET", "").strip()
        if not app_key or not app_secret:
            raise ValueError(
                "Set `TIKTOK_APP_KEY` and `TIKTOK_APP_SECRET` before running the "
                "TikTok OAuth bootstrap."
            )

        raw_cache_file = os.getenv("TIKTOK_TOKEN_CACHE_FILE", "").strip()
        token_cache_file = (
            _resolve_cache_file(raw_cache_file)
            if raw_cache_file
            else ROOT_DIR / TokenCache.CACHE_FILE
        )

        return cls(
            app_key=app_key,
            app_secret=app_secret,
            auth_code=os.getenv("TIKTOK_AUTH_CODE", "").strip(),
            oauth_state=os.getenv("TIKTOK_OAUTH_STATE", "").strip(),
            token_cache_file=token_cache_file,
        )

    def build_oauth(self) -> TikTokOAuth:
        """Create a configured TikTok OAuth helper backed by the configured token cache."""

        return TikTokOAuth(
            self.app_key,
            self.app_secret,
            auth_code=self.auth_code,
            token_cache=TokenCache(self.token_cache_file),
        )
