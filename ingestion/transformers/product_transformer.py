"""Pure product-to-ProductSignals mapping for the standalone ingestion pipeline."""

from __future__ import annotations

from typing import Any

from ingestion.transformers.metrics_transformer import VideoMetrics
from ingestion.transformers.trends_transformer import TrendSignal
from scoring import ProductSignals


def _as_float(value: object, *, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    return default


def transform_product(
    raw: dict[str, Any],
    video_metrics: VideoMetrics,
    trend_signal: TrendSignal,
    days_since_detected: int,
) -> ProductSignals:
    """Map one official TikTok Shop product plus derived source metrics into ProductSignals."""

    price = raw.get("price")
    price_amount = price.get("amount") if isinstance(price, dict) else price
    sales_volume_7d = _as_float(raw.get("sales_volume_7d"))
    return ProductSignals(
        product_id=str(raw.get("product_id", "")),
        name=str(raw.get("title", "")),
        category=str(raw.get("category_name") or "unknown"),
        price=_as_float(price_amount),
        commission_rate=_as_float(raw.get("commission_rate")),
        sales_velocity=sales_volume_7d / 7.0,
        google_trend_score=trend_signal.google_trend_score,
        view_growth_7d=video_metrics.view_growth_7d,
        view_growth_3d=video_metrics.view_growth_3d,
        active_creators=video_metrics.active_creators,
        days_since_detected=max(0, days_since_detected),
        demo_value=video_metrics.demo_value,
        visual_transform=video_metrics.visual_transform,
        hook_clarity=video_metrics.hook_clarity,
    )
