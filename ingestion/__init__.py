"""Standalone multi-source ingestion layer for offline ProductSignals extraction."""

from ingestion.config import IngestionConfig
from ingestion.pipeline import IngestionPipeline
from ingestion.storage import IngestionCache
from ingestion.transformers.metrics_transformer import VideoMetrics, compute_video_metrics
from ingestion.transformers.product_transformer import transform_product
from ingestion.transformers.trends_transformer import TrendSignal, compute_trend_signal

__all__ = [
    "IngestionCache",
    "IngestionConfig",
    "IngestionPipeline",
    "TrendSignal",
    "VideoMetrics",
    "compute_trend_signal",
    "compute_video_metrics",
    "transform_product",
]
