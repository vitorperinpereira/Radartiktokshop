"""Aggregation logic for the standalone deterministic scoring engine."""

from __future__ import annotations

from datetime import UTC, datetime
from math import exp

from scoring.calibration import ScoringParams
from scoring.factors import clamp_score, f_opportunity, f_price, f_revenue, f_trend, f_viral
from scoring.lifecycle import classify_lifecycle
from scoring.models import ProductScore, ProductSignals

EXPLOSIVE = (90, 100)
HIGH = (80, 89)
WORTH_TEST = (70, 79)
NICHE = (60, 69)
LOW = (0, 59)


def estimated_revenue_signal(signals: ProductSignals) -> float:
    """Compute the raw revenue signal used by the requested normalization formula."""

    estimated_commission = signals.price * signals.commission_rate
    return estimated_commission * signals.sales_velocity


def _normalized_commission_rate(commission_rate: float) -> float:
    """Normalize commission rates expressed either as fractions or percentage points."""

    if commission_rate < 0.0:
        return 0.0
    return commission_rate if commission_rate <= 1.0 else commission_rate / 100.0


def _revenue_boost_factor(commission_rate: float) -> float:
    normalized_rate = _normalized_commission_rate(commission_rate)
    if normalized_rate >= 0.30:
        return 1.4
    if normalized_rate >= 0.20:
        return 1.2
    return 1.0


def _google_trends_boost(trend_score: float, signals: ProductSignals) -> float:
    if signals.google_trend_score > 50.0 and trend_score > 70.0:
        return 1.1
    return 1.0


def label_for_score(score: float) -> str:
    """Map a 0-100 score onto the requested interpretation bands."""

    if score >= EXPLOSIVE[0]:
        return "EXPLOSIVE"
    if score >= HIGH[0]:
        return "HIGH"
    if score >= WORTH_TEST[0]:
        return "WORTH_TEST"
    if score >= NICHE[0]:
        return "NICHE"
    return "LOW"


def time_decay(days_since_detected: int, params: ScoringParams) -> float:
    """Compute the post-aggregation temporal decay factor."""

    return exp(-params.lambda_ * max(0, days_since_detected))


def acceleration_bonus(
    growth_3d: float,
    growth_7d: float,
    params: ScoringParams,
) -> float:
    """Compute the post-aggregation acceleration bonus.

    If the seven-day growth baseline is zero or negative, the bonus falls back to
    `1.0` to avoid undefined or unstable ratios.
    """

    if growth_7d <= 0.0:
        return 1.0
    ratio_delta = max(0.0, (growth_3d / growth_7d) - 1.0)
    return min(1.0 + (params.beta * ratio_delta), params.bonus_cap)


def score_product(
    signals: ProductSignals,
    r_max: float,
    params: ScoringParams,
) -> ProductScore:
    """Score one product using the full three-layer deterministic model.

    Layer 1:
    normalize trend, revenue, competition, and viral-content factors to 0-100.

    Layer 2:
    combine those factor scores into a weighted base score.

    Layer 3:
    apply temporal decay and a short-term acceleration bonus, then clamp the
    final score back into the 0-100 range.
    """

    trend_score = f_trend(signals.view_growth_7d, params)
    revenue_score = f_revenue(estimated_revenue_signal(signals), r_max, params)
    revenue_score = clamp_score(revenue_score * _revenue_boost_factor(signals.commission_rate))
    price_score = f_price(signals.price, params)
    opportunity_score = f_opportunity(float(signals.active_creators), params)
    lifecycle_phase = classify_lifecycle(
        growth_7d=signals.view_growth_7d,
        active_creators=signals.active_creators,
        days_since_detected=signals.days_since_detected,
        growth_3d=signals.view_growth_3d,
    )
    viral_score = f_viral(
        signals.demo_value,
        signals.visual_transform,
        signals.hook_clarity,
        params,
    )

    base_score = (
        (trend_score * params.weights["w1"])
        + (revenue_score * params.weights["w2"])
        + (opportunity_score * params.weights["w3"])
        + (viral_score * params.weights["w4"])
        + (price_score * params.weights["w5"])
    )

    decay_factor = time_decay(signals.days_since_detected, params)
    bonus = acceleration_bonus(signals.view_growth_3d, signals.view_growth_7d, params)
    final_score = clamp_score(
        base_score * decay_factor * bonus * _google_trends_boost(trend_score, signals)
    )

    return ProductScore(
        product_id=signals.product_id,
        name=signals.name,
        final_score=final_score,
        base_score=clamp_score(base_score),
        trend_score=trend_score,
        revenue_score=revenue_score,
        price_score=price_score,
        opportunity_score=opportunity_score,
        lifecycle_phase=lifecycle_phase,
        viral_score=viral_score,
        decay_factor=decay_factor,
        acceleration_bonus=bonus,
        label=label_for_score(final_score),
        scored_at=datetime.now(UTC),
    )


def score_batch(
    products: list[ProductSignals],
    params: ScoringParams,
) -> list[ProductScore]:
    """Score a batch after computing the runtime `r_max` from the batch itself."""

    if not products:
        return []

    r_max = max(estimated_revenue_signal(product) for product in products)
    scored_products = [score_product(product, r_max=r_max, params=params) for product in products]
    return sorted(scored_products, key=lambda product: product.final_score, reverse=True)
