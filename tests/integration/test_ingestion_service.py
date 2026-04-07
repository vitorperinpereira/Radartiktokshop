from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select

from services.ingestion.adapters.mock_adapter import load_mock_records
from services.ingestion.contracts import IngestionRecord
from services.ingestion.normalization import build_title_alias
from services.ingestion.service import ingest_records
from services.shared.config import ROOT_DIR, AppSettings
from services.shared.db import IngestionJob, Product, ProductAlias, ProductSnapshot
from services.shared.db.base import Base
from services.shared.db.session import build_engine, build_session_factory


def test_mock_ingestion_persists_job_products_and_snapshots() -> None:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    db_path = temp_dir / f"ingestion-{uuid4().hex}.sqlite3"
    settings = AppSettings(database_url=f"sqlite+pysqlite:///{db_path.as_posix()}")

    engine = build_engine(settings=settings)
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(settings=settings)

    summary = ingest_records(
        load_mock_records(count=2),
        source_name="mock",
        input_type="mock",
        session_factory=session_factory,
    )

    assert summary.records_received == 2
    assert summary.snapshots_created == 2
    assert summary.status == "completed"

    with session_factory() as session:
        jobs = session.scalars(select(IngestionJob)).all()
        products = session.scalars(select(Product)).all()
        snapshots = session.scalars(select(ProductSnapshot)).all()

    assert len(jobs) == 1
    assert jobs[0].status == "completed"
    assert len(products) == 2
    assert len(snapshots) == 2


def test_ingestion_uses_aliases_before_canonical_key_fallback() -> None:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    db_path = temp_dir / f"ingestion-alias-{uuid4().hex}.sqlite3"
    settings = AppSettings(database_url=f"sqlite+pysqlite:///{db_path.as_posix()}")

    engine = build_engine(settings=settings)
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(settings=settings)

    first_batch = [
        IngestionRecord(
            source_name="csv-seed",
            input_type="csv",
            title="Portable Blender Cup",
            brand="BlendGo",
            category="Kitchen",
            subcategory="Drinkware",
            image_url="https://example.com/blender-cup.jpg",
            source_record_id="sku-csv-1",
            captured_at=datetime(2026, 3, 13, 10, 0, tzinfo=UTC),
            price=Decimal("29.90"),
            orders_estimate=180,
            rating=Decimal("4.70"),
            commission_rate=Decimal("12.50"),
            country="BR",
            raw_payload={"title": "Portable Blender Cup", "source_record_id": "sku-csv-1"},
            validation_issues=[],
        )
    ]
    second_batch = [
        IngestionRecord(
            source_name="json-feed",
            input_type="json",
            title="Portable   Blender Cup!!!",
            brand=None,
            category=None,
            subcategory=None,
            image_url=None,
            source_record_id="json-9",
            captured_at=datetime(2026, 3, 13, 11, 0, tzinfo=UTC),
            price=Decimal("27.90"),
            orders_estimate=210,
            rating=Decimal("4.40"),
            commission_rate=Decimal("11.00"),
            country="BR",
            raw_payload={"title": "Portable   Blender Cup!!!", "source_record_id": "json-9"},
            validation_issues=[],
        )
    ]

    first_summary = ingest_records(
        first_batch,
        source_name="csv-seed",
        input_type="csv",
        session_factory=session_factory,
    )
    second_summary = ingest_records(
        second_batch,
        source_name="json-feed",
        input_type="json",
        session_factory=session_factory,
    )

    assert first_summary.products_created == 1
    assert second_summary.products_created == 0

    with session_factory() as session:
        products = session.scalars(select(Product)).all()
        aliases = session.scalars(select(ProductAlias)).all()
        snapshots = session.scalars(select(ProductSnapshot)).all()

    assert len(products) == 1
    assert len(snapshots) == 2
    assert len(aliases) == 3

    source_aliases = {
        (alias.source_name, alias.alias_value)
        for alias in aliases
        if alias.alias_type == "source_record_id"
    }
    title_aliases = [alias for alias in aliases if alias.alias_type == "normalized_title"]

    assert ("csv-seed", "sku-csv-1") in source_aliases
    assert ("json-feed", "json-9") in source_aliases
    assert len(title_aliases) == 1
    assert title_aliases[0].alias_value == build_title_alias("Portable Blender Cup")
