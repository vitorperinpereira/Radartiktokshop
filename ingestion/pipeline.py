"""Concurrent orchestration for the standalone multi-source ingestion flow."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable
from typing import Any

from ingestion.auth import TikTokOAuth
from ingestion.clients import (
    ApifyClient,
    GoogleTrendsClient,
    TikTokShopAuthError,
    TikTokShopClient,
)
from ingestion.config import IngestionConfig
from ingestion.scrapers import (
    GoogleTrendsScraper,
    TikTokShopOfficialScraper,
    TikTokVideosScraper,
)
from ingestion.storage import IngestionCache
from ingestion.transformers import (
    compute_trend_signal,
    compute_video_metrics,
    transform_product,
)
from scoring import ProductSignals

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Fetch raw multi-source payloads, compute metrics, and emit ProductSignals."""

    def __init__(self, config: IngestionConfig) -> None:
        self.config = config
        self.apify_client = ApifyClient(token=config.apify_token)
        self.oauth = TikTokOAuth(
            config.tiktok_app_key,
            config.tiktok_app_secret,
            auth_code=config.tiktok_auth_code,
        )
        self.shop_client = TikTokShopClient(
            self.oauth,
            region=config.tiktok_region,
        )
        self.google_trends_client = GoogleTrendsClient(
            geo=config.google_trends_geo,
            language=config.google_trends_lang,
        )
        self.shop_scraper = TikTokShopOfficialScraper(
            self.shop_client,
            max_products=config.max_products_per_keyword,
        )
        self.videos_scraper = TikTokVideosScraper(
            self.apify_client,
            results_per_page=config.max_videos_per_keyword,
        )
        self.trends_scraper = GoogleTrendsScraper(self.google_trends_client)
        self.cache = IngestionCache(cache_dir=config.cache_dir)

    @staticmethod
    def _previous_days_index(signals: list[ProductSignals] | None) -> dict[str, int]:
        if signals is None:
            return {}
        return {signal.product_id: signal.days_since_detected for signal in signals}

    @staticmethod
    def _estimate_days_since_detected(
        raw_product: dict[str, Any],
        previous_days: dict[str, int],
    ) -> int:
        product_id = str(raw_product.get("product_id", "") or raw_product.get("productId", ""))
        if product_id in previous_days:
            return previous_days[product_id] + 1
        return 0

    async def _fetch_products(self, keyword: str) -> list[dict[str, Any]]:
        try:
            return await self.shop_scraper.fetch(keyword)
        except TikTokShopAuthError:
            logger.error("TikTok Shop API token expired - run: python -m ingestion.auth")
            return []
        except Exception as exc:
            logger.warning("[ingestion] %s: TikTok Shop fetch failed: %s", keyword, exc)
            return []

    async def _fetch_videos(self, keyword: str) -> list[dict[str, Any]]:
        try:
            return await self.videos_scraper.fetch(keyword)
        except Exception as exc:
            logger.warning("[ingestion] %s: TikTok video fetch failed: %s", keyword, exc)
            return []

    async def _fetch_trends(self, keyword: str) -> list[dict[str, Any]]:
        try:
            return await self.trends_scraper.fetch(keyword)
        except Exception as exc:
            logger.warning("[ingestion] %s: Google Trends fetch failed: %s", keyword, exc)
            return []

    async def _process_keyword(
        self,
        keyword: str,
        previous_days: dict[str, int],
    ) -> list[ProductSignals]:
        logger.info("[ingestion] %s: fetching multi-source data", keyword)
        try:
            raw_products, raw_videos, raw_trends = await asyncio.gather(
                self._fetch_products(keyword),
                self._fetch_videos(keyword),
                self._fetch_trends(keyword),
            )
            self.cache.save_raw(keyword, "tiktok_shop", raw_products)
            self.cache.save_raw(keyword, "tiktok_videos", raw_videos)
            self.cache.save_raw(keyword, "google_trends", raw_trends)

            metrics = compute_video_metrics(raw_videos)
            trend_signal = compute_trend_signal(raw_trends)
            signals = [
                transform_product(
                    product,
                    metrics,
                    trend_signal,
                    self._estimate_days_since_detected(product, previous_days),
                )
                for product in sorted(
                    raw_products,
                    key=lambda item: (
                        str(item.get("product_id", "") or item.get("productId", "")),
                        str(item.get("title", "")),
                    ),
                )
            ]
            logger.info("[ingestion] %s: produced %s ProductSignals", keyword, len(signals))
            return signals
        except Exception as exc:
            logger.warning("[ingestion] %s: failed - %s", keyword, exc)
            return []

    @staticmethod
    def _flatten_signal_groups(groups: Iterable[list[ProductSignals]]) -> list[ProductSignals]:
        flattened = [signal for group in groups for signal in group]
        return sorted(flattened, key=lambda signal: (signal.product_id, signal.name))

    async def run(self, keywords: list[str] | None = None) -> list[ProductSignals]:
        """Run the standalone ingestion flow for one or more keywords."""

        keyword_list = keywords if keywords is not None else self.config.keywords
        if not keyword_list:
            self.cache.save_signals([])
            return []

        previous_days = self._previous_days_index(self.cache.load_latest_signals())
        results = await asyncio.gather(
            *(self._process_keyword(keyword, previous_days) for keyword in keyword_list)
        )
        signals = self._flatten_signal_groups(results)
        self.cache.save_signals(signals)
        return signals
