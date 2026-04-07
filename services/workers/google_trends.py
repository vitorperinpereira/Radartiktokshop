"""Google Trends validation worker used by feature extraction."""

from __future__ import annotations

import logging
import threading
import time
from importlib import import_module
from typing import Any

logger = logging.getLogger(__name__)

_MIN_REQUEST_INTERVAL_SECONDS = 2.0
_LAST_REQUEST_AT = 0.0
_THROTTLE_LOCK = threading.Lock()


def _build_trend_req() -> Any | None:
    try:
        module = import_module("pytrends.request")
    except ImportError:
        logger.warning("pytrends is not installed; Google Trends will be skipped.")
        return None

    trend_req = getattr(module, "TrendReq", None)
    if trend_req is None:
        logger.warning("pytrends.request.TrendReq is unavailable; Google Trends will be skipped.")
        return None
    return trend_req(hl="pt-BR", tz=0)


def _throttle() -> None:
    global _LAST_REQUEST_AT
    with _THROTTLE_LOCK:
        now = time.monotonic()
        elapsed = now - _LAST_REQUEST_AT
        if elapsed < _MIN_REQUEST_INTERVAL_SECONDS:
            time.sleep(_MIN_REQUEST_INTERVAL_SECONDS - elapsed)
        _LAST_REQUEST_AT = time.monotonic()


def fetch_trend_score(
    keyword: str,
    geo: str = "BR",
    timeframe: str = "now 7-d",
) -> int | None:
    """Return a 0-100 Google Trends score for a keyword or None on failure."""

    normalized_keyword = keyword.strip()
    if not normalized_keyword:
        return None

    try:
        _throttle()
        trend_req = _build_trend_req()
        if trend_req is None:
            return None

        trend_req.build_payload([normalized_keyword], geo=geo, timeframe=timeframe)
        frame = trend_req.interest_over_time()
        if getattr(frame, "empty", True):
            return None
        if normalized_keyword not in frame:
            return None

        series = frame[normalized_keyword]
        if getattr(series, "empty", False):
            return None
        latest = series.iloc[-1] if hasattr(series, "iloc") else series[-1]
        return max(0, min(100, int(latest)))
    except Exception as exc:
        logger.warning("Google Trends lookup failed for `%s`: %s", normalized_keyword, exc)
        return None
