from __future__ import annotations

import pytest

from scoring import ProductSignals, default_params, score_batch, score_product


def _build_signals(
    *,
    product_id: str,
    name: str,
    price: float,
    commission_rate: float,
    sales_velocity: float,
    view_growth_7d: float,
    view_growth_3d: float,
    active_creators: int,
    days_since_detected: int,
    demo_value: float,
    visual_transform: float,
    hook_clarity: float,
) -> ProductSignals:
    return ProductSignals(
        product_id=product_id,
        name=name,
        category="Beauty",
        price=price,
        commission_rate=commission_rate,
        sales_velocity=sales_velocity,
        view_growth_7d=view_growth_7d,
        view_growth_3d=view_growth_3d,
        active_creators=active_creators,
        days_since_detected=days_since_detected,
        demo_value=demo_value,
        visual_transform=visual_transform,
        hook_clarity=hook_clarity,
    )


def test_score_product_computes_the_full_pipeline() -> None:
    params = default_params()
    signals = _build_signals(
        product_id="product-1",
        name="Heatless Curling Ribbon",
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

    score = score_product(signals, r_max=72.0, params=params)

    assert score.product_id == "product-1"
    assert score.name == "Heatless Curling Ribbon"
    assert score.trend_score == pytest.approx(39.3469340287)
    assert score.revenue_score == pytest.approx(100.0)
    assert score.price_score == pytest.approx(85.5217581281)
    assert score.opportunity_score == pytest.approx(75.5081337596)
    assert score.lifecycle_phase == "PICO"
    assert score.viral_score == pytest.approx(86.7)
    assert score.base_score == pytest.approx(75.0477118847)
    assert score.decay_factor == pytest.approx(0.9417645336)
    assert score.acceleration_bonus == pytest.approx(1.15)
    assert score.final_score == pytest.approx(81.2788643866)
    assert score.label == "HIGH"


def test_score_batch_uses_runtime_r_max_and_returns_descending_scores() -> None:
    params = default_params()
    low_revenue = _build_signals(
        product_id="product-1",
        name="Portable Blender Cup",
        price=25.0,
        commission_rate=0.10,
        sales_velocity=20.0,
        view_growth_7d=8.0,
        view_growth_3d=8.0,
        active_creators=35,
        days_since_detected=4,
        demo_value=70.0,
        visual_transform=65.0,
        hook_clarity=72.0,
    )
    high_revenue = _build_signals(
        product_id="product-2",
        name="Desk Cable Organizer",
        price=40.0,
        commission_rate=0.15,
        sales_velocity=30.0,
        view_growth_7d=12.0,
        view_growth_3d=18.0,
        active_creators=10,
        days_since_detected=1,
        demo_value=86.0,
        visual_transform=82.0,
        hook_clarity=84.0,
    )

    scores = score_batch([low_revenue, high_revenue], params)

    assert [score.product_id for score in scores] == ["product-2", "product-1"]
    assert scores[0].revenue_score == pytest.approx(100.0)
    assert scores[1].revenue_score == pytest.approx(52.7046276695)
    assert scores[0].final_score > scores[1].final_score


def test_acceleration_bonus_applies_only_when_three_day_growth_exceeds_seven_day_growth() -> None:
    params = default_params()
    accelerating = _build_signals(
        product_id="product-1",
        name="Accelerating Product",
        price=18.0,
        commission_rate=0.10,
        sales_velocity=25.0,
        view_growth_7d=10.0,
        view_growth_3d=15.0,
        active_creators=25,
        days_since_detected=3,
        demo_value=82.0,
        visual_transform=76.0,
        hook_clarity=74.0,
    )
    flat = accelerating.model_copy(update={"product_id": "product-2", "view_growth_3d": 10.0})

    accelerating_score = score_product(accelerating, r_max=45.0, params=params)
    flat_score = score_product(flat, r_max=45.0, params=params)

    assert accelerating_score.acceleration_bonus == pytest.approx(1.15)
    assert flat_score.acceleration_bonus == pytest.approx(1.0)
    assert accelerating_score.final_score > flat_score.final_score
