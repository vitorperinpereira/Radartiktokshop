"""Normalization helpers for source ingestion."""

from services.ingestion.normalization.canonical import (
    build_canonical_key,
    build_title_alias,
    normalize_text,
)

__all__ = ["normalize_text", "build_canonical_key", "build_title_alias"]
