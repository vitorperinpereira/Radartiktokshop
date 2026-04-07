"""Lifecycle phase classification for TikTok products."""

from __future__ import annotations


def classify_lifecycle(
    growth_7d: float,
    active_creators: int,
    days_since_detected: int,
    growth_3d: float = 0.0,
) -> str:
    """Classify a product lifecycle phase from growth and creator pressure."""

    if growth_7d < 0.0 or active_creators > 80:
        return "SATURADO"
    if active_creators > 30 and growth_3d < growth_7d:
        return "PICO"
    if growth_7d > 500.0 and 10 <= active_creators <= 30:
        return "ACELERANDO"
    if 200.0 <= growth_7d <= 500.0 and active_creators < 10 and days_since_detected < 14:
        return "EMERGENTE"
    if growth_7d > 200.0 and active_creators < 30:
        return "ACELERANDO"
    if active_creators < 10:
        return "EMERGENTE"
    return "PICO"
