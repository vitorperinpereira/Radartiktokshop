"""Abstract scraper boundary for swappable external ingestion sources."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """Shared async contract for raw-source scrapers."""

    @abstractmethod
    async def fetch(self, keyword: str) -> list[dict[str, object]]:
        """Fetch raw data for a given keyword. Returns raw API items."""


# TODO: add a Bright Data-backed scraper implementation behind the same boundary.
