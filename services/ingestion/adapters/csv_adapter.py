"""CSV ingestion adapter."""

from __future__ import annotations

import csv
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from services.ingestion.contracts import IngestionRecord
from services.ingestion.normalization import normalize_text


def _optional_decimal(value: str | None) -> Decimal | None:
    if not value:
        return None
    return Decimal(value.strip())


def _optional_int(value: str | None) -> int | None:
    if not value:
        return None
    return int(value.strip())


def _optional_str(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = normalize_text(value)
    return value.strip() if normalized else None


def _captured_at(value: str | None) -> datetime:
    if not value:
        return datetime.now(UTC)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_csv_records(csv_path: Path, *, source_name: str | None = None) -> list[IngestionRecord]:
    records: list[IngestionRecord] = []

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=1):
            issues: list[str] = []
            title = (row.get("title") or "").strip()
            if not title:
                title = f"untitled-record-{row_number}"
                issues.append("missing_title")

            raw_country = _optional_str(row.get("country") or row.get("region"))
            record = IngestionRecord(
                source_name=source_name or csv_path.stem,
                input_type="csv",
                title=title,
                brand=_optional_str(row.get("brand")),
                category=_optional_str(row.get("category")),
                subcategory=_optional_str(row.get("subcategory")),
                image_url=_optional_str(row.get("image_url")),
                source_record_id=_optional_str(row.get("source_record_id"))
                or f"{csv_path.stem}-{row_number}",
                captured_at=_captured_at(row.get("captured_at")),
                price=_optional_decimal(row.get("price")),
                orders_estimate=_optional_int(row.get("orders_estimate")),
                rating=_optional_decimal(row.get("rating")),
                commission_rate=_optional_decimal(row.get("commission_rate")),
                country=raw_country.upper() if raw_country else None,
                raw_payload=dict(row),
                validation_issues=issues,
            )
            records.append(record)

    return records
