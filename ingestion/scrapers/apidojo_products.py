"""Apify-backed scraper for TikTok product data via apidojo/tiktok-scraper."""

from __future__ import annotations

from ingestion.clients import ApifyClient
from ingestion.scrapers.base import BaseScraper


class ApidojoProductScraper(BaseScraper):
    """Fetch raw TikTok Shop product listings using the apidojo/tiktok-scraper actor.

    Input schema (actor: apidojo/tiktok-scraper):
        keyword      – search term
        searchSection – "/search/item" for product results
        maxItems     – result cap
        region       – "BR" for Brazil pricing/catalog
    """

    ACTOR_ID = "apidojo~tiktok-scraper"

    def __init__(self, client: ApifyClient, max_products: int = 100) -> None:
        self.client = client
        self.max_products = max_products

    async def fetch(self, keyword: str) -> list[dict[str, object]]:
        """Run the actor and return raw product items for one keyword."""

        return await self.client.run_and_collect(
            self.ACTOR_ID,
            {
                "keyword": keyword,
                "searchSection": "/search/item",
                "maxItems": self.max_products,
                "region": "BR",
                "proxyConfiguration": {
                    "useApifyProxy": True,
                    "apifyProxyGroups": ["RESIDENTIAL"],
                    "apifyProxyCountry": "BR"
                },
            },
        )
