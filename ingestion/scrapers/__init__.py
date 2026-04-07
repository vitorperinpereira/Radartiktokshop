"""Source scrapers for the standalone ingestion package."""

from ingestion.scrapers.apidojo_products import ApidojoProductScraper
from ingestion.scrapers.base import BaseScraper
from ingestion.scrapers.clockworks_videos import ClockworksVideosScraper
from ingestion.scrapers.google_trends import GoogleTrendsScraper
from ingestion.scrapers.pro100chok_shop import Pro100chokShopScraper
from ingestion.scrapers.tiktok_shop import TikTokShopScraper
from ingestion.scrapers.tiktok_shop_official import TikTokShopOfficialScraper
from ingestion.scrapers.tiktok_videos import TikTokVideosScraper

__all__ = [
    "ApidojoProductScraper",
    "BaseScraper",
    "ClockworksVideosScraper",
    "GoogleTrendsScraper",
    "Pro100chokShopScraper",
    "TikTokShopOfficialScraper",
    "TikTokShopScraper",
    "TikTokVideosScraper",
]
