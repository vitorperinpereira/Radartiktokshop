"""Apify-backed scraper for TikTok video metrics via clockworks/tiktok-scraper."""

from __future__ import annotations

from ingestion.clients import ApifyClient
from ingestion.scrapers.base import BaseScraper


class ClockworksVideosScraper(BaseScraper):
    """Fetch raw TikTok video metrics for a keyword using clockworks/tiktok-scraper.

    Used to enrich product records with engagement signals (views, likes, shares).
    Raw items are stored in raw_payload and fed into ProductSignal — NOT used
    to create new Product rows.

    Input schema (actor: clockworks/tiktok-scraper):
        searchQueries – list of keyword strings
        maxItems      – result cap per query
        shouldDownloadVideos – false (skip video download)

    Output fields (flexible):
        id                 – video id
        desc               – video description / product mention
        stats.playCount    – view count
        stats.diggCount    – like count
        stats.shareCount   – share count
        stats.commentCount – comment count
        authorMeta.name    – creator handle
        createTime         – Unix timestamp
        hashtags           – list of {name}
    """

    ACTOR_ID = "clockworks~tiktok-scraper"

    def __init__(self, client: ApifyClient, max_items: int = 50) -> None:
        self.client = client
        self.max_items = max_items

    async def fetch(self, keyword: str) -> list[dict[str, object]]:
        """Run the actor and return raw video items for one keyword."""

        return await self.client.run_and_collect(
            self.ACTOR_ID,
            {
                "searchQueries": [keyword],
                "resultsPerPage": self.max_items,
                "proxyConfiguration": {
                    "useApifyProxy": True,
                    "apifyProxyGroups": ["RESIDENTIAL"],
                    "apifyProxyCountry": "BR"
                },
                "shouldDownloadVideos": False,
                "shouldDownloadCovers": False,
                "region": "BR",
            },
        )
