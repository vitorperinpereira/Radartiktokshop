from __future__ import annotations

import re

import pytest

from ranking import RankingFilters, RankingService
from scoring import ProductSignals


def _build_product(index: int) -> ProductSignals:
    return ProductSignals(
        product_id=f"product-{index}",
        name=f"Product {index}",
        category="beauty" if index % 2 == 0 else "fitness",
        price=20.0 + index,
        commission_rate=0.05 + (index * 0.005),
        sales_velocity=10.0 + index,
        view_growth_7d=5.0 + index,
        view_growth_3d=4.0 + (index * 1.1),
        active_creators=20 + index,
        days_since_detected=index % 15,
        demo_value=50.0 + index,
        visual_transform=45.0 + index,
        hook_clarity=40.0 + index,
    )


def test_generate_ranking_returns_correct_count() -> None:
    products = [_build_product(index) for index in range(30)]

    report = RankingService().generate_ranking(products, top_n=10)

    assert report.total_products_analyzed == 30
    assert report.top_n == 10
    assert len(report.entries) == 10


def test_ranking_is_sorted_descending() -> None:
    products = [_build_product(index) for index in range(12)]

    report = RankingService().generate_ranking(products, top_n=12)

    assert report.entries[0].rank == 1
    assert report.entries[0].final_score >= report.entries[1].final_score
    assert report.entries == sorted(
        report.entries,
        key=lambda entry: entry.final_score,
        reverse=True,
    )


def test_week_label_format() -> None:
    report = RankingService().generate_ranking([_build_product(1)])

    assert re.fullmatch(r"\d{4}-W\d{2}", report.week_label) is not None


def test_estimated_commission_calculation() -> None:
    product = ProductSignals(
        product_id="product-1",
        name="Known Commission Product",
        category="beauty",
        price=20.0,
        commission_rate=0.10,
        sales_velocity=15.0,
        view_growth_7d=10.0,
        view_growth_3d=12.0,
        active_creators=25,
        days_since_detected=3,
        demo_value=85.0,
        visual_transform=80.0,
        hook_clarity=75.0,
    )

    report = RankingService().generate_ranking([product])

    assert report.entries[0].estimated_weekly_commission == 210.0


def test_filters_applied_correctly() -> None:
    products = [
        ProductSignals(
            product_id="explosive-product",
            name="Explosive Product",
            category="beauty",
            price=30.0,
            commission_rate=0.12,
            sales_velocity=40.0,
            view_growth_7d=120.0,
            view_growth_3d=180.0,
            active_creators=5,
            days_since_detected=0,
            demo_value=100.0,
            visual_transform=100.0,
            hook_clarity=100.0,
        ),
        ProductSignals(
            product_id="low-product",
            name="Low Product",
            category="fitness",
            price=15.0,
            commission_rate=0.04,
            sales_velocity=5.0,
            view_growth_7d=1.0,
            view_growth_3d=1.0,
            active_creators=140,
            days_since_detected=21,
            demo_value=25.0,
            visual_transform=20.0,
            hook_clarity=30.0,
        ),
    ]
    filters = RankingFilters(min_score=80.0)

    report = RankingService().generate_ranking(products, top_n=10, filters=filters)

    assert report.filters_applied == {"min_score": 80.0}
    assert report.entries
    assert [entry.product_id for entry in report.entries] == ["explosive-product"]
    assert all(entry.final_score >= 80.0 for entry in report.entries)


def test_empty_input_returns_empty_report() -> None:
    report = RankingService().generate_ranking([], top_n=10)

    assert report.total_products_analyzed == 0
    assert report.top_n == 0
    assert report.entries == []


def test_duplicate_product_ids_raise_value_error() -> None:
    products = [
        ProductSignals(
            product_id="duplicate-product",
            name="Duplicate A",
            category="beauty",
            price=20.0,
            commission_rate=0.10,
            sales_velocity=10.0,
            view_growth_7d=4.0,
            view_growth_3d=4.0,
            active_creators=10,
            days_since_detected=2,
            demo_value=70.0,
            visual_transform=65.0,
            hook_clarity=60.0,
        ),
        ProductSignals(
            product_id="duplicate-product",
            name="Duplicate B",
            category="fitness",
            price=25.0,
            commission_rate=0.12,
            sales_velocity=12.0,
            view_growth_7d=6.0,
            view_growth_3d=7.0,
            active_creators=12,
            days_since_detected=1,
            demo_value=80.0,
            visual_transform=75.0,
            hook_clarity=70.0,
        ),
    ]

    with pytest.raises(ValueError, match="unique `product_id`"):
        RankingService().generate_ranking(products)
