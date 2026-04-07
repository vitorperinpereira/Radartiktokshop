"""Media proxy and local cache for TikTok CDN URLs.

TikTok CDN URLs expire in minutes. This service downloads media immediately
on request, caches it locally, and serves it from cache on subsequent requests.
"""

from __future__ import annotations

import hashlib
import logging
import mimetypes
import os
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# Directory where cached media files are stored
CACHE_DIR = Path(os.environ.get("MEDIA_CACHE_DIR", "media_cache")).resolve()
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Browser-like headers so TikTok CDN accepts our requests
_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Referer": "https://www.tiktok.com/",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "cross-site",
}

_MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit per file
_TIMEOUT_S = 12.0
_RETRIES = 2


def _url_to_cache_path(url: str) -> Path:
    """Derive a stable cache filename from the URL using a SHA-1 hash."""
    digest = hashlib.sha1(url.encode(), usedforsecurity=False).hexdigest()
    # Try to preserve the original extension for correct Content-Type later
    path_part = url.split("?")[0].rstrip("/")
    ext = Path(path_part).suffix[:8]  # cap to avoid weirdly long extensions
    if not ext or len(ext) > 6:
        ext = ".jpg"
    return CACHE_DIR / f"{digest}{ext}"


def _sniff_content_type(path: Path, fallback: str = "image/jpeg") -> str:
    guessed, _ = mimetypes.guess_type(str(path))
    return guessed or fallback


async def fetch_and_cache(url: str) -> tuple[Path, str] | None:
    """Download *url* to the local cache (if not already cached).

    Returns ``(local_path, content_type)`` on success, ``None`` on failure.
    The file is written atomically so concurrent requests don't serve partial data.
    """
    if not url or not url.startswith("http"):
        return None

    cache_path = _url_to_cache_path(url)

    if cache_path.exists() and cache_path.stat().st_size > 0:
        return cache_path, _sniff_content_type(cache_path)

    for attempt in range(1, _RETRIES + 1):
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=_TIMEOUT_S,
                headers=_BROWSER_HEADERS,
            ) as client:
                async with client.stream("GET", url) as response:
                    if response.status_code != 200:
                        logger.warning(
                            "media_cache: HTTP %s for %s (attempt %s/%s)",
                            response.status_code,
                            url[:80],
                            attempt,
                            _RETRIES,
                        )
                        continue

                    content_type = response.headers.get("content-type", "image/jpeg").split(";")[0]
                    tmp_path = cache_path.with_suffix(".tmp")
                    size = 0
                    with tmp_path.open("wb") as fh:
                        async for chunk in response.aiter_bytes(chunk_size=32_768):
                            size += len(chunk)
                            if size > _MAX_SIZE_BYTES:
                                logger.warning("media_cache: file too large, aborting %s", url[:80])
                                tmp_path.unlink(missing_ok=True)
                                return None
                            fh.write(chunk)

                    tmp_path.rename(cache_path)
                    logger.debug(
                        "media_cache: cached %s → %s (%d bytes)", url[:60], cache_path.name, size
                    )
                    return cache_path, content_type

        except (httpx.TimeoutException, httpx.RequestError) as exc:
            logger.warning(
                "media_cache: attempt %s/%s failed for %s: %s", attempt, _RETRIES, url[:80], exc
            )

    return None


def get_cached(url: str) -> tuple[Path, str] | None:
    """Return cached file synchronously (no download). ``None`` if not cached."""
    if not url:
        return None
    cache_path = _url_to_cache_path(url)
    if cache_path.exists() and cache_path.stat().st_size > 0:
        return cache_path, _sniff_content_type(cache_path)
    return None


def cache_size_mb() -> float:
    """Return total size of the media cache in megabytes."""
    total = sum(f.stat().st_size for f in CACHE_DIR.iterdir() if f.is_file())
    return round(total / 1_048_576, 2)
