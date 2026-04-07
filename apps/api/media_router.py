"""Media proxy router — serves TikTok CDN images via local cache.

Endpoint: GET /api/media/proxy?url=<encoded_tiktok_url>

Why: TikTok CDN URLs expire in minutes. Serving via this proxy downloads the
image on first request, caches it locally, and returns it with long-lived
Cache-Control headers so the browser caches it too.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, Response

from services.media.cache import cache_size_mb, fetch_and_cache, get_cached

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/proxy")
async def media_proxy(url: str = Query(..., description="Original TikTok CDN URL")):
    """Download (if needed) and serve a TikTok media file from local cache."""
    if not url or not url.startswith("http"):
        raise HTTPException(status_code=400, detail="url inválida")

    # Return from cache immediately if available
    cached = get_cached(url)
    if cached:
        path, content_type = cached
        return FileResponse(
            path=str(path),
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=86400, immutable",
                "X-Cache": "HIT",
            },
        )

    # Download and cache
    result = await fetch_and_cache(url)
    if result is None:
        # Return transparent 1×1 PNG placeholder instead of 404
        # so broken images don't cause layout shifts
        PLACEHOLDER = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        return Response(
            content=PLACEHOLDER,
            media_type="image/png",
            headers={"Cache-Control": "no-store", "X-Cache": "MISS-FAIL"},
        )

    path, content_type = result
    return FileResponse(
        path=str(path),
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=86400, immutable",
            "X-Cache": "MISS",
        },
    )


@router.get("/cache-stats")
async def cache_stats():
    """Return current media cache size."""
    return {"cache_size_mb": cache_size_mb()}
