"""Official TikTok Shop Partner API scraper adapter."""

from __future__ import annotations

from ingestion.clients import TikTokShopClient
from ingestion.scrapers.base import BaseScraper


class TikTokShopOfficialScraper(BaseScraper):
    """Fetch raw TikTok Shop products for one keyword via the official Partner API."""

    def __init__(self, client: TikTokShopClient, max_products: int = 100) -> None:
        self.client = client
        self.max_products = max_products

    async def fetch(self, keyword: str) -> list[dict[str, object]]:
        """Call the official TikTok Shop product search endpoint."""

        return await self.client.search_products(keyword, page_size=self.max_products)
