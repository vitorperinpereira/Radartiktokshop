"""JSON ingestion adapter for array-based payloads."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from services.ingestion.contracts import IngestionRecord
from services.ingestion.normalization import normalize_text


def _optional_decimal(value: object) -> Decimal | None:
    if value in (None, ""):
        return None
    return Decimal(str(value).strip())


def _optional_int(value: object) -> int | None:
    if value in (None, ""):
        return None
    return int(str(value).strip())


def _optional_str(value: object) -> str | None:
    if value is None:
        return None

    raw_value = str(value).strip()
    if not normalize_text(raw_value):
        return None
    return raw_value


def _captured_at(value: object) -> datetime:
    if value in (None, ""):
        return datetime.now(UTC)
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _validation_issues(payload: dict[str, Any]) -> list[str]:
    raw_issues = payload.get("validation_issues")
    if not isinstance(raw_issues, list):
        return []
    return [str(item).strip() for item in raw_issues if str(item).strip()]


def load_json_records(
    json_path: Path,
    *,
    source_name: str | None = None,
) -> list[IngestionRecord]:
    with json_path.open("r", encoding="utf-8-sig") as handle:
        payload: object = json.load(handle)

    if not isinstance(payload, list):
        raise ValueError("JSON ingestion expects a top-level array of objects.")

    records: list[IngestionRecord] = []
    for row_number, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            raise ValueError(
                f"JSON ingestion expects objects only. Invalid item at index {row_number}."
            )

        row = {str(key): value for key, value in item.items()}
        issues = _validation_issues(row)
        title = _optional_str(row.get("title")) or f"untitled-record-{row_number}"
        if title.startswith("untitled-record-"):
            issues.append("missing_title")

        raw_country = _optional_str(row.get("country") or row.get("region"))
        record = IngestionRecord(
            source_name=source_name or json_path.stem,
            input_type="json",
            title=title,
            brand=_optional_str(row.get("brand")),
            category=_optional_str(row.get("category")),
            subcategory=_optional_str(row.get("subcategory")),
            image_url=_optional_str(row.get("image_url")),
            source_record_id=_optional_str(row.get("source_record_id"))
            or f"{json_path.stem}-{row_number}",
            captured_at=_captured_at(row.get("captured_at")),
            price=_optional_decimal(row.get("price")),
            orders_estimate=_optional_int(row.get("orders_estimate")),
            rating=_optional_decimal(row.get("rating")),
            commission_rate=_optional_decimal(row.get("commission_rate")),
            country=raw_country.upper() if raw_country else None,
            raw_payload=row,
            validation_issues=issues,
        )
        records.append(record)

    return records
