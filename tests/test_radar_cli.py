from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session, sessionmaker

from bin import radar
from ingestion.config import IngestionConfig
from services.ingestion.contracts import IngestionRecord, IngestionSummary
from services.shared.config import AppSettings


def test_build_apify_record_maps_supported_fields() -> None:
    raw_product = {
        "productId": "product-123",
        "title": "LED Strip Lights",
        "brandName": "Glowify",
        "categoryName": "Home",
        "subCategory": "Lighting",
        "mainImage": {"url": "https://example.com/led-strip.jpg"},
        "price": "29.90",
        "soldCount": "125",
        "ratingAverage": "4.80",
        "commissionRate": "12.5",
        "createTime": 1_710_000_000,
    }

    record = radar._build_apify_record(raw_product, keyword="led strip")

    assert record.source_name == "apify"
    assert record.input_type == "apify"
    assert record.title == "LED Strip Lights"
    assert record.brand == "Glowify"
    assert record.category == "Home"
    assert record.subcategory == "Lighting"
    assert record.image_url == "https://example.com/led-strip.jpg"
    assert record.source_record_id == "product-123"
    assert record.price == Decimal("29.90")
    assert record.orders_estimate == 125
    assert record.rating == Decimal("4.80")
    assert record.commission_rate == Decimal("12.5")
    assert record.captured_at == datetime.fromtimestamp(1_710_000_000, tz=UTC)
    assert record.raw_payload["apify_keyword"] == "led strip"


def test_ingest_apify_command_persists_records_and_reports_summary(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fetched_record = IngestionRecord(
        source_name="apify",
        input_type="apify",
        title="Mini Massager",
        brand="PulseLab",
        category="Wellness",
        subcategory=None,
        image_url="https://example.com/massager.jpg",
        source_record_id="product-1",
        captured_at=datetime(2026, 3, 18, 12, 0, tzinfo=UTC),
        price=Decimal("19.90"),
        orders_estimate=80,
        rating=Decimal("4.60"),
        commission_rate=Decimal("10.00"),
        country="BR",
        raw_payload={"productId": "product-1", "apify_keyword": "led strip"},
        validation_issues=[],
    )

    observed: dict[str, object] = {}

    monkeypatch.setenv("APIFY_TOKEN", "secret")
    monkeypatch.setenv("TIKTOK_APP_KEY", "app-key")
    monkeypatch.setenv("TIKTOK_APP_SECRET", "app-secret")
    monkeypatch.setenv("TIKTOK_AUTH_CODE", "auth-code")
    monkeypatch.setenv("INGESTION_KEYWORDS", "env keyword")
    monkeypatch.setattr(
        radar,
        "get_settings",
        lambda: AppSettings(database_url="sqlite+pysqlite:///:memory:"),
    )
    monkeypatch.setattr(radar, "configure_logging", lambda level: None)

    async def fake_load_apify_records(
        loaded_config: IngestionConfig,
        *,
        keywords: list[str],
    ) -> tuple[list[IngestionRecord], list[str]]:
        assert loaded_config.apify_token == "secret"
        assert loaded_config.keywords == ["env keyword"]
        assert keywords == ["led strip", "mini massager"]
        return [fetched_record], ["broken-keyword"]

    def fake_ingest_records(
        records: Iterable[IngestionRecord],
        *,
        source_name: str,
        input_type: str,
        session_factory: sessionmaker[Session],
    ) -> IngestionSummary:
        observed["records"] = list(records)
        observed["source_name"] = source_name
        observed["input_type"] = input_type
        observed["session_factory"] = session_factory
        return IngestionSummary(
            job_id="job-123",
            source_name=source_name,
            input_type=input_type,
            records_received=1,
            records_written=1,
            products_created=1,
            products_updated=0,
            snapshots_created=1,
            validation_issue_count=0,
            status="completed",
        )

    monkeypatch.setattr(radar, "_load_apify_records", fake_load_apify_records)
    monkeypatch.setattr(radar, "ingest_records", fake_ingest_records)

    exit_code = radar.main(["ingest-apify", "--keywords", "led strip, mini massager"])

    assert exit_code == 0
    assert observed["source_name"] == "apify"
    assert observed["input_type"] == "apify"
    assert observed["records"] == [fetched_record]

    stdout = capsys.readouterr().out
    payload = json.loads(
        "\n".join(line for line in stdout.splitlines() if not line.startswith("[ingestion]"))
    )
    assert payload["status"] == "completed"
    assert payload["command"] == "ingest-apify"
    assert payload["keywords"] == ["led strip", "mini massager"]
    assert payload["failed_keywords"] == ["broken-keyword"]
    assert payload["records_fetched"] == 1
