"""Synchronous wrapper around `pytrends` for Brazilian keyword signals."""

from __future__ import annotations

import logging
import time
from importlib import import_module
from typing import Any

logger = logging.getLogger(__name__)


def _is_rate_limit_error(exc: Exception) -> bool:
    name = exc.__class__.__name__.lower()
    message = str(exc).lower()
    return "ratelimit" in name or ("too" in name and "request" in name) or "429" in message


class GoogleTrendsClient:
    """Thin wrapper for Google Trends lookups scoped to Brazil."""

    def __init__(self, geo: str = "BR", language: str = "pt-BR") -> None:
        self.geo = geo
        self.language = language

    def _build_trend_req(self) -> Any | None:
        try:
            module = import_module("pytrends.request")
        except ImportError:
            logger.warning(
                "`pytrends` is not installed; Google Trends lookups will return empty data."
            )
            return None
        trend_req = getattr(module, "TrendReq", None)
        if trend_req is None:
            logger.warning("`pytrends.request.TrendReq` is unavailable; using empty data.")
            return None
        return trend_req(hl=self.language, tz=0)

    def get_interest_over_time(
        self,
        keyword: str,
        timeframe: str = "now 7-d",
    ) -> dict[str, int]:
        """Return `interest_over_time()` as a simple date/value mapping."""

        for attempt in range(1, 4):
            try:
                trend_req = self._build_trend_req()
                if trend_req is None:
                    return {}
                trend_req.build_payload([keyword], timeframe=timeframe, geo=self.geo)
                frame = trend_req.interest_over_time()
                if getattr(frame, "empty", True):
                    return {}
                if keyword not in frame:
                    return {}
                series = frame[keyword]
                return {str(index): int(value) for index, value in series.items()}
            except Exception as exc:
                if _is_rate_limit_error(exc) and attempt < 3:
                    logger.warning("Google Trends rate limit reached for `%s`; retrying.", keyword)
                    time.sleep(60)
                    continue
                if _is_rate_limit_error(exc):
                    logger.warning(
                        "Google Trends rate limit reached for `%s`; using empty data.",
                        keyword,
                    )
                else:
                    logger.warning("Google Trends lookup failed for `%s`: %s", keyword, exc)
                return {}
        return {}

    def get_related_queries(self, keyword: str) -> dict[str, object]:
        """Return the `related_queries()` payload for a keyword."""

        try:
            trend_req = self._build_trend_req()
            if trend_req is None:
                return {}
            trend_req.build_payload([keyword], timeframe="now 7-d", geo=self.geo)
            payload = trend_req.related_queries()
            return payload if isinstance(payload, dict) else {}
        except Exception as exc:
            logger.warning("Google Trends related queries failed for `%s`: %s", keyword, exc)
            return {}

    def get_trending_searches(self) -> list[str]:
        """Return today's trending searches in Brazil."""

        try:
            trend_req = self._build_trend_req()
            if trend_req is None:
                return []
            frame = trend_req.trending_searches(pn="brazil")
            if getattr(frame, "empty", True):
                return []
            if hasattr(frame, "iloc"):
                values = frame.iloc[:, 0].tolist()
                return [str(value) for value in values]
            if isinstance(frame, list):
                return [str(value) for value in frame]
            return []
        except Exception as exc:
            logger.warning("Google Trends trending searches failed: %s", exc)
            return []
