from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select

from services.shared.config import ROOT_DIR, AppSettings
from services.shared.db import Base, Product, ProductSignal, ProductSnapshot
from services.shared.db.session import build_engine, build_session_factory
from services.workers.feature_extraction import (
    build_signal_candidates,
    extract_latest_snapshot_signals,
)


def test_build_signal_candidates_emits_expected_metrics() -> None:
    snapshot = ProductSnapshot(
        id="snapshot-1",
        product_id="product-1",
        source_name="mock-demo_weekly",
        source_record_id="sku-1",
        captured_at=datetime(2026, 3, 13, 10, 0, tzinfo=UTC),
        price=Decimal("29.90"),
        orders_estimate=180,
        rating=Decimal("4.70"),
        commission_rate=Decimal("12.50"),
        raw_payload={"title": "Portable Blender Cup", "stock_count": 5000},
        created_at=datetime(2026, 3, 13, 10, 0, tzinfo=UTC),
    )

    candidates = build_signal_candidates(snapshot)
    signal_map = {candidate.signal_name: candidate for candidate in candidates}

    assert len(candidates) == 6
    assert signal_map["price_current"].signal_value == Decimal("29.90")
    assert signal_map["orders_estimate_current"].signal_value == Decimal("180")
    assert signal_map["rating_current"].signal_value == Decimal("4.70")
    assert signal_map["commission_rate_current"].signal_value == Decimal("12.50")
    assert signal_map["stock_count"].signal_value == Decimal("5000")
    assert signal_map["revenue_proxy_current"].signal_value == Decimal("5382.00")


def test_extract_latest_snapshot_signals_adds_google_trends_when_available(
    monkeypatch,
) -> None:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    db_path = temp_dir / f"feature-extraction-{uuid4().hex}.sqlite3"
    settings = AppSettings(database_url=f"sqlite+pysqlite:///{db_path.as_posix()}")

    engine = build_engine(settings=settings)
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(settings=settings)

    monkeypatch.setattr(
        "services.workers.feature_extraction.fetch_trend_score",
        lambda keyword: 77,
    )

    with session_factory() as session:
        session.add(
            Product(
                id="product-1",
                canonical_key="demo::product",
                title="Portable Blender Cup",
                brand=None,
                category="Kitchen",
                subcategory=None,
                image_url=None,
                status="active",
            )
        )
        session.add(
            ProductSnapshot(
                id="snapshot-1",
                product_id="product-1",
                source_name="mock-demo_weekly",
                source_record_id="sku-1",
                captured_at=datetime(2026, 3, 13, 10, 0, tzinfo=UTC),
                price=Decimal("29.90"),
                orders_estimate=180,
                rating=Decimal("4.70"),
                commission_rate=Decimal("12.50"),
                raw_payload={"title": "Portable Blender Cup", "stock_count": 5000},
                created_at=datetime(2026, 3, 13, 10, 0, tzinfo=UTC),
            )
        )
        session.commit()

    with session_factory() as session:
        summary = extract_latest_snapshot_signals(session)
        session.commit()
        signals = session.scalars(select(ProductSignal)).all()

    assert summary.signals_created == 7
    assert any(signal.signal_name == "google_trends_score" for signal in signals)
