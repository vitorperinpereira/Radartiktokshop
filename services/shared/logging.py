"""Logging helpers for local development."""

from __future__ import annotations

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure a simple process-wide logging format."""

    resolved_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=resolved_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        force=True,
    )
