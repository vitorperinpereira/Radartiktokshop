"""Canonical key and text normalization helpers."""

from __future__ import annotations

import re

_SPACE_RE = re.compile(r"\s+")
_NON_WORD_RE = re.compile(r"[^a-z0-9]+")


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""

    cleaned = value.strip().lower()
    cleaned = _SPACE_RE.sub(" ", cleaned)
    cleaned = _NON_WORD_RE.sub("-", cleaned)
    cleaned = cleaned.strip("-")
    return cleaned


def build_canonical_key(title: str, brand: str | None, category: str | None) -> str:
    segments = [normalize_text(title), normalize_text(brand), normalize_text(category)]
    filtered_segments = [segment for segment in segments if segment]
    return "::".join(filtered_segments) or "unknown-product"


def build_title_alias(title: str) -> str:
    return normalize_text(title)
