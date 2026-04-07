from __future__ import annotations

from decimal import Decimal

from scoring.gmv_estimator import estimate_gmv_from_snapshots


def test_estimate_gmv_from_snapshots_uses_inventory_delta() -> None:
    snapshots = [
        {"stock_count": 5000, "price": 20},
        {"stock_count": 4500, "price": 20},
    ]

    assert estimate_gmv_from_snapshots(snapshots) == Decimal("10000")


def test_estimate_gmv_from_snapshots_ignores_restocking() -> None:
    snapshots = [
        {"stock_count": 4500, "price": 20},
        {"stock_count": 5000, "price": 20},
    ]

    assert estimate_gmv_from_snapshots(snapshots) == Decimal("0")


def test_estimate_gmv_from_snapshots_requires_multiple_snapshots() -> None:
    assert estimate_gmv_from_snapshots([{"stock_count": 100, "price": 10}]) is None


def test_estimate_gmv_from_snapshots_skips_incomplete_rows() -> None:
    snapshots = [
        {"stock_count": 100, "price": 10},
        {"stock_count": None, "price": 10},
        {"stock_count": 20, "price": None},
    ]

    assert estimate_gmv_from_snapshots(snapshots) is None


def test_estimate_gmv_from_snapshots_returns_none_when_price_is_missing() -> None:
    snapshots = [
        {"stock_count": 100, "price": None},
        {"stock_count": 20, "price": None},
    ]

    assert estimate_gmv_from_snapshots(snapshots) is None
