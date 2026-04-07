"""Persistence-aware ingestion service."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from services.ingestion.adapters.creator_extractor import (
    extract_creators_from_video_payload,
    persist_creators,
)
from services.ingestion.contracts import IngestionRecord, IngestionSummary
from services.ingestion.normalization import build_canonical_key, build_title_alias
from services.shared.db.models import IngestionJob, Product, ProductAlias, ProductSnapshot


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _build_job_metadata(records: list[IngestionRecord]) -> dict[str, object]:
    return {
        "validation_issue_count": sum(len(record.validation_issues) for record in records),
        "sources": sorted({record.source_name for record in records}),
    }


def _json_safe(value: object) -> object:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _source_record_alias(record: IngestionRecord) -> tuple[str, str, str] | None:
    if not record.source_record_id:
        return None
    return ("source_record_id", record.source_record_id, record.source_name)


def _normalized_title_alias(record: IngestionRecord) -> tuple[str, str, None] | None:
    alias_value = build_title_alias(record.title)
    if not alias_value:
        return None
    return ("normalized_title", alias_value, None)


def _find_product_by_alias(session: Session, record: IngestionRecord) -> Product | None:
    source_alias = _source_record_alias(record)
    if source_alias is not None:
        alias_type, alias_value, alias_source = source_alias
        source_match = (
            session.execute(
                select(Product)
                .join(ProductAlias)
                .where(
                    ProductAlias.alias_type == alias_type,
                    ProductAlias.alias_value == alias_value,
                    ProductAlias.source_name == alias_source,
                )
            )
            .scalars()
            .first()
        )
        if source_match is not None:
            return source_match

    title_alias = _normalized_title_alias(record)
    if title_alias is None:
        return None

    alias_type, alias_value, _ = title_alias
    return (
        session.execute(
            select(Product)
            .join(ProductAlias)
            .where(
                ProductAlias.alias_type == alias_type,
                ProductAlias.alias_value == alias_value,
            )
        )
        .scalars()
        .first()
    )


def _ensure_alias(
    session: Session,
    *,
    product_id: str,
    alias_type: str,
    alias_value: str,
    source_name: str | None,
) -> None:
    existing = (
        session.execute(
            select(ProductAlias).where(
                ProductAlias.product_id == product_id,
                ProductAlias.alias_type == alias_type,
                ProductAlias.alias_value == alias_value,
                ProductAlias.source_name == source_name,
            )
        )
        .scalars()
        .first()
    )
    if existing is not None:
        return

    session.add(
        ProductAlias(
            id=str(uuid4()),
            product_id=product_id,
            alias_type=alias_type,
            alias_value=alias_value,
            source_name=source_name,
            created_at=_utcnow(),
        )
    )


def _register_record_aliases(session: Session, product: Product, record: IngestionRecord) -> None:
    for alias in (_source_record_alias(record), _normalized_title_alias(record)):
        if alias is None:
            continue
        alias_type, alias_value, alias_source = alias
        _ensure_alias(
            session,
            product_id=product.id,
            alias_type=alias_type,
            alias_value=alias_value,
            source_name=alias_source,
        )


def _maybe_refresh_canonical_key(
    session: Session,
    *,
    product: Product,
    incoming_key: str,
) -> bool:
    if incoming_key == product.canonical_key:
        return False

    existing_with_key = session.execute(
        select(Product).where(
            Product.canonical_key == incoming_key,
            Product.id != product.id,
        )
    ).scalar_one_or_none()
    if existing_with_key is not None:
        return False

    if incoming_key.count("::") < product.canonical_key.count("::"):
        return False

    product.canonical_key = incoming_key
    return True


def _upsert_product(session: Session, record: IngestionRecord) -> tuple[Product, str]:
    canonical_key = build_canonical_key(record.title, record.brand, record.category)
    existing = _find_product_by_alias(session, record)
    if existing is None:
        existing = session.execute(
            select(Product).where(Product.canonical_key == canonical_key)
        ).scalar_one_or_none()

    if existing is None:
        product = Product(
            id=str(uuid4()),
            canonical_key=canonical_key,
            title=record.title,
            brand=record.brand,
            category=record.category,
            subcategory=record.subcategory,
            image_url=record.image_url,
            status="active",
        )
        session.add(product)
        session.flush()
        _register_record_aliases(session, product, record)
        return product, "created"

    updated = _maybe_refresh_canonical_key(
        session,
        product=existing,
        incoming_key=canonical_key,
    )
    for field_name in ("title", "brand", "category", "subcategory", "image_url"):
        incoming_value = getattr(record, field_name)
        current_value = getattr(existing, field_name)
        if incoming_value and incoming_value != current_value:
            setattr(existing, field_name, incoming_value)
            updated = True

    _register_record_aliases(session, existing, record)
    return existing, "updated" if updated else "unchanged"


_REQUIRED_COUNTRY = "BR"


def _gate_record(record: IngestionRecord, logger: logging.Logger) -> bool:
    """Return True if the record passes all ingestion quality gates.

    Gates (all must pass):
    - commission_rate, if present, must be > 0 (skip only explicit zero/negative commission)
    - orders_estimate must be present and > 0 (product must have sales history)
    - country, if present, must be 'BR' (Brazil-only ingestion)
    """
    import decimal

    commission = record.commission_rate
    if commission is not None and (
        (isinstance(commission, decimal.Decimal) and commission <= 0) or commission <= 0
    ):
        logger.debug(
            "Skipping record %s — explicit zero/negative commission (commission_rate=%s)",
            record.source_record_id,
            commission,
        )
        return False

    orders = record.orders_estimate
    if orders is None or orders <= 0:
        logger.debug(
            "Skipping record %s — no sales (orders_estimate=%s)",
            record.source_record_id,
            orders,
        )
        return False

    if record.country is not None and record.country.upper() != _REQUIRED_COUNTRY:
        logger.debug(
            "Skipping record %s — non-BR country (%s)",
            record.source_record_id,
            record.country,
        )
        return False

    return True


def ingest_records(
    records: Iterable[IngestionRecord],
    *,
    source_name: str,
    input_type: str,
    session_factory: sessionmaker[Session],
) -> IngestionSummary:
    import logging as _logging

    _gate_logger = _logging.getLogger(__name__)
    all_records = list(records)
    prepared_records = [r for r in all_records if _gate_record(r, _gate_logger)]
    started_at = _utcnow()
    job_id = str(uuid4())
    validation_issue_count = sum(len(record.validation_issues) for record in prepared_records)

    with session_factory() as session:
        job = IngestionJob(
            id=job_id,
            source_name=source_name,
            input_type=input_type,
            status="running",
            records_received=len(all_records),
            records_written=0,
            started_at=started_at,
            finished_at=None,
            metadata_json={
                **_build_job_metadata(prepared_records),
                "records_received_total": len(all_records),
                "records_after_gates": len(prepared_records),
                "records_skipped_by_gates": len(all_records) - len(prepared_records),
            },
        )
        session.add(job)
        session.commit()

    products_created = 0
    products_updated = 0
    snapshots_created = 0

    try:
        with session_factory() as session:
            persisted_job = session.get(IngestionJob, job_id)
            if persisted_job is None:
                raise RuntimeError(f"Ingestion job `{job_id}` was not persisted.")

            for record in prepared_records:
                try:
                    with session.begin_nested():
                        product, product_state = _upsert_product(session, record)
                        products_created += int(product_state == "created")
                        products_updated += int(product_state == "updated")

                        snapshot = ProductSnapshot(
                            id=str(uuid4()),
                            product_id=product.id,
                            source_name=record.source_name,
                            source_record_id=record.source_record_id,
                            captured_at=record.captured_at,
                            price=record.price,
                            orders_estimate=record.orders_estimate,
                            rating=record.rating,
                            commission_rate=record.commission_rate,
                            country=record.country,
                            raw_payload=_json_safe(record.raw_payload),
                            created_at=_utcnow(),
                        )
                        session.add(snapshot)
                        snapshots_created += 1

                        creators = extract_creators_from_video_payload(record.raw_payload)
                        if creators:
                            persist_creators(session, creators, product_id=product.id)
                except Exception as exc:
                    _gate_logger.warning(
                        "Failed to ingest record %s: %s",
                        getattr(record, "source_record_id", ""),
                        exc,
                    )
                    continue

            persisted_job.status = "completed"
            persisted_job.records_written = snapshots_created
            persisted_job.finished_at = _utcnow()
            persisted_job.metadata_json = {
                **persisted_job.metadata_json,
                "products_created": products_created,
                "products_updated": products_updated,
                "snapshots_created": snapshots_created,
            }
            session.commit()
    except Exception as exc:
        with session_factory() as session:
            failed_job = session.get(IngestionJob, job_id)
            if failed_job is not None:
                failed_job.status = "failed"
                failed_job.finished_at = _utcnow()
                failed_job.metadata_json = {
                    **failed_job.metadata_json,
                    "error": str(exc),
                }
                session.commit()
        raise

    return IngestionSummary(
        job_id=job_id,
        source_name=source_name,
        input_type=input_type,
        records_received=len(all_records),
        records_written=snapshots_created,
        products_created=products_created,
        products_updated=products_updated,
        snapshots_created=snapshots_created,
        validation_issue_count=validation_issue_count,
        status="completed",
    )
