"""Async scraper adapter for synchronous Google Trends lookups."""

from __future__ import annotations

import asyncio

from ingestion.clients import GoogleTrendsClient
from ingestion.scrapers.base import BaseScraper


class GoogleTrendsScraper(BaseScraper):
    """Fetch normalized Google Trends values for one keyword."""

    def __init__(self, client: GoogleTrendsClient) -> None:
        self.client = client

    async def fetch(self, keyword: str) -> list[dict[str, object]]:
        """Return interest-over-time points as `[{date, value}]` records."""

        interest_map = await asyncio.to_thread(self.client.get_interest_over_time, keyword)
        return [
            {"date": date, "value": int(value)}
            for date, value in interest_map.items()
        ]
