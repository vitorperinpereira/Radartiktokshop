"""Apify-backed scraper for TikTok hashtag video metrics."""

from __future__ import annotations

from ingestion.clients import ApifyClient
from ingestion.scrapers.base import BaseScraper


class TikTokVideosScraper(BaseScraper):
    """Fetch raw TikTok videos for one keyword using the shared Apify client."""

    ACTOR_ID = "apidojo~tiktok-scraper"

    def __init__(self, client: ApifyClient, results_per_page: int = 50) -> None:
        self.client = client
        self.results_per_page = results_per_page

    async def fetch(self, keyword: str) -> list[dict[str, object]]:
        """Call the TikTok video actor and return raw video items."""

        return await self.client.run_and_collect(
            self.ACTOR_ID,
            {
                "searchSection": "/search/video",
                "maxItems": self.results_per_page,
                "region": "BR",
                "keyword": keyword,
            },
        )
