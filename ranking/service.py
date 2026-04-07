"""Stateless offline ranking service built on top of the standalone scorer."""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from uuid import uuid4

from ranking.filters import RankingFilters, apply_filters
from ranking.models import RankingEntry, RankingReport
from scoring import ProductSignals, ScoringParams, default_params, score_batch


class RankingService:
    """Generate offline ranking reports from in-memory product signals."""

    def __init__(self, params: ScoringParams | None = None) -> None:
        self._params = params if params is not None else default_params()

    def generate_ranking(
        self,
        products: list[ProductSignals],
        top_n: int = 50,
        filters: RankingFilters | None = None,
    ) -> RankingReport:
        """Score a batch, apply filters, and return a populated ranking report.

        The offline scorer only carries `product_id` back in `ProductScore`, so the
        incoming batch must use unique product identifiers to preserve a safe
        one-to-one join between raw signals and scored outputs.
        """

        if top_n < 0:
            raise ValueError("`top_n` must be greater than or equal to zero.")
        product_ids = [product.product_id for product in products]
        if len(set(product_ids)) != len(product_ids):
            raise ValueError("`products` must contain unique `product_id` values.")

        generated_at = datetime.now(UTC)
        iso_week = generated_at.isocalendar()
        week_label = f"{iso_week.year}-W{iso_week.week:02d}"

        total_products_analyzed = len(products)
        scores = score_batch(products, self._params) if products else []
        product_by_id = {product.product_id: product for product in products}
        ordered_products = [product_by_id[score.product_id] for score in scores]

        applied_filters = filters or RankingFilters()
        if filters is not None:
            ordered_products, scores = apply_filters(ordered_products, scores, filters)

        limited_products = ordered_products[:top_n]
        limited_scores = scores[:top_n]
        entries: list[RankingEntry] = []
        for rank, (product, score) in enumerate(
            zip(limited_products, limited_scores, strict=True),
            start=1,
        ):
            entries.append(
                RankingEntry(
                    rank=rank,
                    product_id=score.product_id,
                    name=score.name,
                    category=product.category,
                    final_score=score.final_score,
                    label=score.label,
                    trend_score=score.trend_score,
                    revenue_score=score.revenue_score,
                    competition_score=score.competition_score,
                    viral_score=score.viral_score,
                    decay_factor=score.decay_factor,
                    acceleration_bonus=score.acceleration_bonus,
                    estimated_weekly_commission=(
                        product.price * product.commission_rate * product.sales_velocity * 7.0
                    ),
                    days_since_detected=product.days_since_detected,
                    scored_at=score.scored_at,
                )
            )

        return RankingReport(
            report_id=str(uuid4()),
            generated_at=generated_at,
            week_label=week_label,
            total_products_analyzed=total_products_analyzed,
            top_n=len(entries),
            filters_applied=applied_filters.model_dump(exclude_none=True),
            params_used=asdict(self._params),
            entries=entries,
        )
