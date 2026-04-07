"""Environment-driven settings for the standalone ingestion package."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

TOKEN_CACHE_FILE = ".cache/auth/tiktok_token.json"

ROOT_DIR = Path(__file__).resolve().parents[1]
logger = logging.getLogger(__name__)


def _parse_keywords(raw_value: str | None) -> list[str]:
    if raw_value is None:
        return []
    return [keyword.strip() for keyword in raw_value.split(",") if keyword.strip()]


@dataclass(frozen=True, slots=True)
class IngestionConfig:
    """Runtime settings for the standalone multi-source ingestion flow."""

    apify_token: str
    keywords: list[str]
    tiktok_app_key: str = ""
    tiktok_app_secret: str = ""
    tiktok_auth_code: str = ""
    tiktok_region: str = "BR"
    google_trends_geo: str = "BR"
    google_trends_lang: str = "pt-BR"
    max_products_per_keyword: int = 100
    max_videos_per_keyword: int = 50
    cache_dir: str = ".cache/ingestion"
    days_lookback: int = 30

    # ── Ingestion backend ───────────────────────────────────────────────────
    # "apify"    → use the three Apify scrapers below (current mode)
    # "official" → use TikTok Shop Partner API (post-approval)
    ingestion_backend: str = "apify"

    # ── Apify actor IDs (swappable without code changes) ───────────────────
    apify_actor_products: str = "apidojo~tiktok-scraper"
    apify_actor_shop: str = "pro100chok~tiktok-shop-scraper-usage"
    apify_actor_videos: str = "clockworks~tiktok-scraper"

    @classmethod
    def from_env(cls) -> IngestionConfig:
        """Load ingestion settings from `.env` and process environment variables."""

        load_dotenv(ROOT_DIR / ".env")
        apify_token = os.getenv("APIFY_TOKEN", "").strip()
        backend = os.getenv("INGESTION_BACKEND", "apify").strip().lower() or "apify"

        # APIFY_TOKEN is required only when using the Apify backend.
        if backend == "apify" and not apify_token:
            raise ValueError("`APIFY_TOKEN` must be set when `INGESTION_BACKEND=apify`.")

        tiktok_app_key = os.getenv("TIKTOK_APP_KEY", "").strip()
        tiktok_app_secret = os.getenv("TIKTOK_APP_SECRET", "").strip()
        if backend == "official" and (not tiktok_app_key or not tiktok_app_secret):
            raise ValueError(
                "Set `TIKTOK_APP_KEY` and `TIKTOK_APP_SECRET` before running ingestion. "
                "Create the app at `https://partner.tiktokshop.com` and authenticate with "
                "`python -m ingestion.auth`."
            )

        token_cache_path = ROOT_DIR / TOKEN_CACHE_FILE
        if backend == "official" and not token_cache_path.exists():
            logger.warning(
                "[ingestion] TikTok Shop token cache not found. "
                "Run `python -m ingestion.auth` after configuring `TIKTOK_AUTH_CODE`."
            )

        return cls(
            apify_token=apify_token,
            keywords=_parse_keywords(os.getenv("INGESTION_KEYWORDS")),
            tiktok_app_key=tiktok_app_key,
            tiktok_app_secret=tiktok_app_secret,
            tiktok_auth_code=os.getenv("TIKTOK_AUTH_CODE", "").strip(),
            tiktok_region=os.getenv("TIKTOK_REGION", "BR").strip() or "BR",
            google_trends_geo=os.getenv("GOOGLE_TRENDS_GEO", "BR").strip() or "BR",
            google_trends_lang=os.getenv("GOOGLE_TRENDS_LANG", "pt-BR").strip() or "pt-BR",
            max_products_per_keyword=int(
                os.getenv("INGESTION_MAX_PRODUCTS_PER_KEYWORD", "100")
            ),
            max_videos_per_keyword=int(os.getenv("INGESTION_MAX_VIDEOS_PER_KEYWORD", "50")),
            cache_dir=os.getenv("INGESTION_CACHE_DIR", ".cache/ingestion"),
            days_lookback=int(os.getenv("INGESTION_DAYS_LOOKBACK", "30")),
            ingestion_backend=backend,
            apify_actor_products=os.getenv(
                "APIFY_ACTOR_PRODUCTS", "apidojo~tiktok-scraper"
            ).strip(),
            apify_actor_shop=os.getenv(
                "APIFY_ACTOR_SHOP", "pro100chok~tiktok-shop-scraper-usage"
            ).strip(),
            apify_actor_videos=os.getenv(
                "APIFY_ACTOR_VIDEOS", "clockworks~tiktok-scraper"
            ).strip(),
        )
