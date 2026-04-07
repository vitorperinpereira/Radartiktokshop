"""Typed contracts for ingestion adapters and persistence flows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class IngestionRecord:
    source_name: str
    input_type: str
    title: str
    brand: str | None
    category: str | None
    subcategory: str | None
    image_url: str | None
    source_record_id: str | None
    captured_at: datetime
    price: Decimal | None
    orders_estimate: int | None
    rating: Decimal | None
    commission_rate: Decimal | None
    country: str | None
    raw_payload: dict[str, Any]
    validation_issues: list[str] = field(default_factory=list)

    def as_metadata(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["captured_at"] = self.captured_at.isoformat()
        payload["price"] = None if self.price is None else str(self.price)
        payload["rating"] = None if self.rating is None else str(self.rating)
        payload["commission_rate"] = (
            None if self.commission_rate is None else str(self.commission_rate)
        )
        return payload


@dataclass(frozen=True)
class IngestionSummary:
    job_id: str
    source_name: str
    input_type: str
    records_received: int
    records_written: int
    products_created: int
    products_updated: int
    snapshots_created: int
    validation_issue_count: int
    status: str
