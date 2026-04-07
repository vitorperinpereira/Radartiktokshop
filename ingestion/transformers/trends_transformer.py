"""Google Trends signal normalization for the standalone ingestion pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TrendSignal:
    """Normalized Google Trends signal for one keyword."""

    google_trend_score: float
    trend_velocity: float
    is_accelerating: bool


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / float(len(values))


def compute_trend_signal(interest_data: list[dict[str, object]]) -> TrendSignal:
    """Compute a Google Trends score plus short-term acceleration signal."""

    values: list[float] = []
    for item in interest_data:
        raw_value = item.get("value")
        if isinstance(raw_value, (int, float)):
            values.append(float(raw_value))
    if not values:
        return TrendSignal(google_trend_score=0.0, trend_velocity=1.0, is_accelerating=False)

    google_trend_score = max(0.0, min(100.0, values[-1]))
    if len(values) < 6:
        return TrendSignal(
            google_trend_score=google_trend_score,
            trend_velocity=1.0,
            is_accelerating=False,
        )

    recent_avg = _mean(values[-3:])
    previous_avg = _mean(values[-6:-3])
    if previous_avg <= 0.0:
        velocity = 1.0
    else:
        velocity = recent_avg / previous_avg

    return TrendSignal(
        google_trend_score=google_trend_score,
        trend_velocity=velocity,
        is_accelerating=velocity > 1.1,
    )
