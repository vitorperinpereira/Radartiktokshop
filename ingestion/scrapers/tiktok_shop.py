"""Apify-backed scraper for TikTok Shop product search results."""

from __future__ import annotations

from ingestion.clients import ApifyClient
from ingestion.scrapers.base import BaseScraper


class TikTokShopScraper(BaseScraper):
    """Fetch raw TikTok Shop product search results for one keyword."""

    ACTOR_ID = "pratikdani~tiktok-shop-search-scraper"

    def __init__(self, client: ApifyClient, max_products: int = 100) -> None:
        self.client = client
        self.max_products = max_products

    async def fetch(self, keyword: str) -> list[dict[str, object]]:
        """Call the TikTok Shop Apify actor and return raw product items."""

        return await self.client.run_and_collect(
            self.ACTOR_ID,
            {
                "searchQuery": keyword,
                "maxProducts": self.max_products,
            },
        )
