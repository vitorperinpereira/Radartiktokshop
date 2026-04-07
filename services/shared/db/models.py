"""Core ORM models for the initial persistence schema."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.shared.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


def _uuid_str() -> str:
    return str(uuid4())


class Product(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (Index("ix_products_canonical_key", "canonical_key", unique=True),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    canonical_key: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subcategory: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    aliases: Mapped[list[ProductAlias]] = relationship(back_populates="product")
    snapshots: Mapped[list[ProductSnapshot]] = relationship(back_populates="product")
    signals: Mapped[list[ProductSignal]] = relationship(back_populates="product")
    scores: Mapped[list[ProductScore]] = relationship(back_populates="product")
    content_angles: Mapped[list[ContentAngle]] = relationship(back_populates="product")
    creator_links: Mapped[list[CreatorProduct]] = relationship(back_populates="product")


class ProductAlias(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "product_aliases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    alias_type: Mapped[str] = mapped_column(String(64), nullable=False)
    alias_value: Mapped[str] = mapped_column(String(500), nullable=False)
    source_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    product: Mapped[Product] = relationship(back_populates="aliases")


class ProductSnapshot(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "product_snapshots"
    __table_args__ = (
        Index("ix_product_snapshots_product_id_captured_at", "product_id", "captured_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    source_name: Mapped[str] = mapped_column(String(128), nullable=False)
    source_record_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    orders_estimate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    commission_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    country: Mapped[str | None] = mapped_column(String(8), nullable=True)
    raw_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    product: Mapped[Product] = relationship(back_populates="snapshots")


class Creator(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "creators"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    handle: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    tier: Mapped[str | None] = mapped_column(String(64), nullable=True)
    primary_niche: Mapped[str | None] = mapped_column(String(128), nullable=True)
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    creator_links: Mapped[list[CreatorProduct]] = relationship(back_populates="creator")


class CreatorProduct(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "creator_products"
    __table_args__ = (
        UniqueConstraint("creator_id", "product_id", name="uq_creator_products_creator_product"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    creator_id: Mapped[str] = mapped_column(ForeignKey("creators.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    creator: Mapped[Creator] = relationship(back_populates="creator_links")
    product: Mapped[Product] = relationship(back_populates="creator_links")


class ProductSignal(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "product_signals"
    __table_args__ = (
        Index(
            "ix_product_signals_product_id_signal_name_observed_at",
            "product_id",
            "signal_name",
            "observed_at",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    signal_name: Mapped[str] = mapped_column(String(128), nullable=False)
    signal_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    signal_type: Mapped[str] = mapped_column(String(64), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    evidence: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    source_kind: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    product: Mapped[Product] = relationship(back_populates="signals")


class IngestionJob(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    source_name: Mapped[str] = mapped_column(String(128), nullable=False)
    input_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    records_received: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_written: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata",
        JSON,
        nullable=False,
        default=dict,
    )


class PipelineRun(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    input_job_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    config_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    scores: Mapped[list[ProductScore]] = relationship(back_populates="run")
    content_angles: Mapped[list[ContentAngle]] = relationship(back_populates="run")
    reports: Mapped[list[Report]] = relationship(back_populates="run")


class ProductScore(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "product_scores"
    __table_args__ = (
        Index("ix_product_scores_week_start_final_score", "week_start", "final_score"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    run_id: Mapped[str] = mapped_column(ForeignKey("pipeline_runs.id"), nullable=False)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    trend_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    viral_potential_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    creator_accessibility_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    saturation_penalty: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    revenue_estimate: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    final_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    classification: Mapped[str | None] = mapped_column(String(64), nullable=True)
    lifecycle_phase: Mapped[str | None] = mapped_column(String(32), nullable=True)
    explainability_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    product: Mapped[Product] = relationship(back_populates="scores")
    run: Mapped[PipelineRun] = relationship(back_populates="scores")


class ContentAngle(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "content_angles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    run_id: Mapped[str] = mapped_column(ForeignKey("pipeline_runs.id"), nullable=False)
    angle_type: Mapped[str] = mapped_column(String(64), nullable=False)
    hook_text: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    product: Mapped[Product] = relationship(back_populates="content_angles")
    run: Mapped[PipelineRun] = relationship(back_populates="content_angles")


class Report(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "reports"
    __table_args__ = (Index("ix_reports_week_start", "week_start"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    run_id: Mapped[str] = mapped_column(ForeignKey("pipeline_runs.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    report_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    run: Mapped[PipelineRun] = relationship(back_populates="reports")


class GarageItem(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "garage_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planejando")
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    product: Mapped[Product] = relationship()

