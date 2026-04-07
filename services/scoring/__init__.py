"""Opportunity scoring and explainability logic."""

from services.scoring.aggregation import (
    SCORE_POLICY_VERSION,
    AggregatedProductScore,
    aggregate_score_input,
    classify_final_score,
    persist_aggregated_scores,
)

__all__ = [
    "AggregatedProductScore",
    "SCORE_POLICY_VERSION",
    "aggregate_score_input",
    "classify_final_score",
    "persist_aggregated_scores",
]
