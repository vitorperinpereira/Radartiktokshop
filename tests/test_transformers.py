from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from ingestion.transformers import TrendSignal
from ingestion.transformers.metrics_transformer import VideoMetrics, compute_video_metrics
from ingestion.transformers.product_transformer import transform_product


def test_transform_product_new_field_paths() -> None:
    raw_product = {
        "product_id": "123",
        "title": "Mini Massager",
        "category_name": "wellness",
        "price": {"amount": 29.9, "currency": "BRL"},
        "commission_rate": 0.15,
        "sales_volume_7d": 70,
    }
    metrics = VideoMetrics(
        view_growth_7d=0.8,
        view_growth_3d=0.4,
        active_creators=12,
        demo_value=70.0,
        visual_transform=60.0,
        hook_clarity=55.0,
    )
    trend_signal = TrendSignal(google_trend_score=77.0, trend_velocity=1.3, is_accelerating=True)

    signal = transform_product(raw_product, metrics, trend_signal, days_since_detected=3)

    assert signal.product_id == "123"
    assert signal.name == "Mini Massager"
    assert signal.category == "wellness"
    assert signal.price == pytest.approx(29.9)
    assert signal.commission_rate == pytest.approx(0.15)
    assert signal.sales_velocity == pytest.approx(10.0)
    assert signal.google_trend_score == pytest.approx(77.0)
    assert signal.days_since_detected == 3


def test_sales_velocity_uses_7d_data() -> None:
    signal = transform_product(
        {
            "product_id": "product-1",
            "title": "Heatless Curling Ribbon",
            "category_name": "beauty",
            "price": {"amount": 20.0, "currency": "BRL"},
            "commission_rate": 0.1,
            "sales_volume_7d": 70,
        },
        VideoMetrics(0.0, 0.0, 0, 0.0, 0.0, 0.0),
        TrendSignal(0.0, 1.0, False),
        days_since_detected=0,
    )

    assert signal.sales_velocity == pytest.approx(10.0)


def test_google_trend_score_injected_correctly() -> None:
    signal = transform_product(
        {
            "product_id": "product-1",
            "title": "LED Strip",
            "category_name": "home",
            "price": {"amount": 19.9, "currency": "BRL"},
            "commission_rate": 0.12,
            "sales_volume_7d": 14,
        },
        VideoMetrics(0.0, 0.0, 0, 0.0, 0.0, 0.0),
        TrendSignal(82.0, 1.4, True),
        days_since_detected=1,
    )

    assert signal.google_trend_score == pytest.approx(82.0)


def test_metrics_transformer_handles_apidojo_format() -> None:
    now = datetime.now(UTC)
    videos = [
        {
            "id": "recent",
            "createTime": int((now - timedelta(days=1)).timestamp()),
            "author": {"id": "author-1", "followerCount": 1_000},
            "stats": {
                "playCount": 100,
                "diggCount": 50,
                "shareCount": 10,
                "commentCount": 5,
            },
            "desc": "demo",
        },
        {
            "id": "old",
            "createTime": int((now - timedelta(days=9)).timestamp()),
            "author": {"id": "author-2", "followerCount": 2_000},
            "stats": {
                "playCount": 50,
                "diggCount": 20,
                "shareCount": 5,
                "commentCount": 2,
            },
            "desc": "demo old",
        },
    ]

    metrics = compute_video_metrics(videos)

    assert metrics.active_creators == 2
    assert metrics.view_growth_7d == pytest.approx(100 / 150)
    assert metrics.view_growth_3d == pytest.approx(100 / 150)


def test_metrics_transformer_new_stats_paths() -> None:
    now = datetime.now(UTC)
    metrics = compute_video_metrics(
        [
            {
                "id": "video-1",
                "createTime": int(now.timestamp()),
                "author": {"id": "author-1", "followerCount": 1_000},
                "stats": {
                    "playCount": 100,
                    "diggCount": 60,
                    "shareCount": 20,
                    "commentCount": 10,
                },
                "desc": "good hook",
            }
        ]
    )

    assert metrics.demo_value == pytest.approx(100.0)
    assert metrics.visual_transform == pytest.approx(100.0)
    assert metrics.hook_clarity == pytest.approx(100.0)
