"""Apify-backed scraper for TikTok Shop data via pro100chok/tiktok-shop-scraper-usage.

Uses a Brazil proxy to return BR-specific pricing, commissions, and sales data.
"""

from __future__ import annotations

from ingestion.clients import ApifyClient
from ingestion.scrapers.base import BaseScraper


class Pro100chokShopScraper(BaseScraper):
    """Fetch raw TikTok Shop product data for Brazil market.

    Input schema (actor: pro100chok/tiktok-shop-scraper-usage):
        queries  – list of keyword strings (required)
        maxItems – result cap per query
        country  – "BR"

    Output fields (flexible — actor may vary):
        itemId / productId / id
        title / name / productName
        price / salePrice / priceInfo.salePrice
        commissionRate / commissionPercent
        soldCount / salesVolume / ordersCount
        rating / ratingAverage
        coverUrl / imageUrl / mainImage
        shopName / sellerName / brand
        category / categoryName
    """

    ACTOR_ID = "pro100chok~tiktok-shop-scraper-usage"

    def __init__(self, client: ApifyClient, max_products: int = 100) -> None:
        self.client = client
        self.max_products = max_products

    async def fetch(self, keyword: str) -> list[dict[str, object]]:
        """Run the actor and return raw shop items for one keyword."""

        return await self.client.run_and_collect(
            self.ACTOR_ID,
            {
                "queries": [keyword],
                "maxItems": self.max_products,
                "country": "BR",
                "proxyConfiguration": {
                    "useApifyProxy": True,
                    "apifyProxyGroups": ["RESIDENTIAL"],
                    "apifyProxyCountry": "BR"
                },
            },
        )
