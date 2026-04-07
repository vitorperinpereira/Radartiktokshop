"""Shared health payload builders."""

from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import urlparse

from services.shared.config import AppSettings


def _database_target(database_url: str) -> str:
    parsed = urlparse(database_url)
    if not parsed.scheme or not parsed.hostname:
        return "unconfigured"

    database_name = parsed.path.lstrip("/") or "unknown"
    port = parsed.port or 5432
    return f"{parsed.scheme}://{parsed.hostname}:{port}/{database_name}"


def build_health_payload(settings: AppSettings, surface: str) -> dict[str, object]:
    """Return a consistent health payload for all runtime surfaces."""

    return {
        "status": "ok",
        "surface": surface,
        "app": settings.app_name,
        "environment": settings.app_env,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "database_target": _database_target(settings.database_url),
        "model_provider": settings.model_provider,
        "seed_profile": settings.seed_profile,
        "default_agent_count": settings.default_agent_count,
    }
