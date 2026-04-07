"""Deterministic workers for ingestion, scoring, and reporting."""

from services.workers.feature_extraction import (
    FEATURE_SOURCE_KIND,
    FeatureExtractionSummary,
    SignalCandidate,
    build_signal_candidates,
    extract_latest_snapshot_signals,
)
from services.workers.google_trends import fetch_trend_score

__all__ = [
    "FEATURE_SOURCE_KIND",
    "SignalCandidate",
    "FeatureExtractionSummary",
    "build_signal_candidates",
    "extract_latest_snapshot_signals",
    "fetch_trend_score",
]
