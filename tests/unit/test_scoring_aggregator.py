from __future__ import annotations

import pytest

from scoring import ProductSignals, default_params, score_product


def test_score_product_includes_price_signal_in_the_base_score() -> None:
    signals = ProductSignals(
        product_id="product-1",
        name="Heatless Curling Ribbon",
        category="Beauty",
        price=20.0,
        commission_rate=0.12,
        sales_velocity=30.0,
        view_growth_7d=10.0,
        view_growth_3d=15.0,
        active_creators=20,
        days_since_detected=2,
        demo_value=88.0,
        visual_transform=90.0,
        hook_clarity=80.0,
    )

    score = score_product(signals, r_max=72.0, params=default_params())

    assert score.price_score == pytest.approx(85.5217581281)
    assert score.opportunity_score == pytest.approx(75.5081337596)
    assert score.lifecycle_phase == "PICO"
    assert score.base_score == pytest.approx(75.0477118847)
    assert score.final_score == pytest.approx(81.2788643866)


def test_score_product_boosts_revenue_for_higher_commission_rates() -> None:
    common_kwargs = dict(
        name="Commission Test Product",
        category="Beauty",
        price=20.0,
        sales_velocity=30.0,
        view_growth_7d=10.0,
        view_growth_3d=12.0,
        active_creators=15,
        days_since_detected=1,
        demo_value=70.0,
        visual_transform=65.0,
        hook_clarity=60.0,
    )

    low_commission = ProductSignals(
        product_id="product-low",
        commission_rate=0.10,
        **common_kwargs,
    )
    high_commission = ProductSignals(
        product_id="product-high",
        commission_rate=0.30,
        **common_kwargs,
    )

    low_score = score_product(low_commission, r_max=72.0, params=default_params())
    high_score = score_product(high_commission, r_max=72.0, params=default_params())

    assert high_score.revenue_score > low_score.revenue_score


def test_score_product_boosts_for_strong_google_trends_validation() -> None:
    common_kwargs = dict(
        name="Trend Validation Product",
        category="Beauty",
        price=20.0,
        commission_rate=0.20,
        sales_velocity=30.0,
        view_growth_7d=25.0,
        view_growth_3d=30.0,
        active_creators=15,
        days_since_detected=1,
        demo_value=70.0,
        visual_transform=65.0,
        hook_clarity=60.0,
    )

    weak_validation = ProductSignals(
        product_id="product-weak",
        google_trend_score=40.0,
        **common_kwargs,
    )
    strong_validation = ProductSignals(
        product_id="product-strong",
        google_trend_score=60.0,
        **common_kwargs,
    )

    weak_score = score_product(weak_validation, r_max=72.0, params=default_params())
    strong_score = score_product(strong_validation, r_max=72.0, params=default_params())

    assert strong_score.final_score > weak_score.final_score
