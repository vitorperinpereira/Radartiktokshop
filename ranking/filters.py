"""Filter helpers for offline ranking generation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from scoring import ProductScore, ProductSignals


class RankingFilters(BaseModel):
    """Optional filters applied after the offline scorer sorts the batch."""

    model_config = ConfigDict(extra="forbid")

    min_score: float | None = Field(default=None, ge=0.0, le=100.0)
    max_active_creators: int | None = Field(default=None, ge=0)
    categories: list[str] | None = None
    min_commission_rate: float | None = Field(default=None, ge=0.0)
    max_days_since_detected: int | None = Field(default=None, ge=0)
    labels: list[str] | None = None


def apply_filters(
    products: list[ProductSignals],
    scores: list[ProductScore],
    filters: RankingFilters,
) -> tuple[list[ProductSignals], list[ProductScore]]:
    """Filter products and scores in lockstep while preserving their order."""

    if len(products) != len(scores):
        raise ValueError("Products and scores must have the same length.")

    normalized_categories = (
        None
        if filters.categories is None
        else {category.lower() for category in filters.categories}
    )
    normalized_labels = (
        None if filters.labels is None else {label.upper() for label in filters.labels}
    )

    filtered_products: list[ProductSignals] = []
    filtered_scores: list[ProductScore] = []
    for product, score in zip(products, scores, strict=True):
        if filters.min_score is not None and score.final_score < filters.min_score:
            continue
        if (
            filters.max_active_creators is not None
            and product.active_creators > filters.max_active_creators
        ):
            continue
        if (
            normalized_categories is not None
            and product.category.lower() not in normalized_categories
        ):
            continue
        if (
            filters.min_commission_rate is not None
            and product.commission_rate < filters.min_commission_rate
        ):
            continue
        if (
            filters.max_days_since_detected is not None
            and product.days_since_detected > filters.max_days_since_detected
        ):
            continue
        if normalized_labels is not None and score.label.upper() not in normalized_labels:
            continue

        filtered_products.append(product)
        filtered_scores.append(score)

    return filtered_products, filtered_scores
