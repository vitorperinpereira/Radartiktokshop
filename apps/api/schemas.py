"""Pydantic response models for the FastAPI read surface."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RankingItem(BaseModel):
    product_id: str
    run_id: str
    week_start: str
    title: str
    brand: str | None
    category: str | None
    subcategory: str | None
    image_url: str | None
    final_score: float | None
    classification: str | None
    trend_score: float | None
    viral_potential_score: float | None
    creator_accessibility_score: float | None
    saturation_penalty: float | None
    revenue_estimate: float | None
    saturation_risk: str
    lifecycle_phase: str | None = None
    opportunity_window_days: int | None = None
    risk_flags: list[str] = Field(default_factory=list)
    summary: str | None = None
    summary_text: str | None = None


class RankingResponse(BaseModel):
    week_start: str | None
    count: int
    items: list[RankingItem]


class ProductMetadata(BaseModel):
    id: str
    canonical_key: str
    title: str
    brand: str | None
    category: str | None
    subcategory: str | None
    image_url: str | None
    status: str


class ProductScoreDetail(BaseModel):
    run_id: str
    week_start: str
    trend_score: float | None
    viral_potential_score: float | None
    creator_accessibility_score: float | None
    saturation_penalty: float | None
    revenue_estimate: float | None
    final_score: float | None
    classification: str | None
    lifecycle_phase: str | None = None
    opportunity_window_days: int | None = None
    google_trends_score: float | None = None
    summary_text: str | None = None
    saturation_risk: str
    risk_flags: list[str] = Field(default_factory=list)
    explainability_payload: dict[str, object]


class SnapshotMetadata(BaseModel):
    captured_at: str
    price: float | None
    orders_estimate: int | None
    rating: float | None
    commission_rate: float | None
    source_name: str
    source_record_id: str | None


class ProductDetailResponse(BaseModel):
    product: ProductMetadata
    score: ProductScoreDetail
    latest_snapshot: SnapshotMetadata | None
    summary_text: str | None = None
    lifecycle_phase: str | None = None
    opportunity_window_days: int | None = None
    google_trends_score: float | None = None
    gmv_estimate: float | None = None
    content_angles: list[ContentAngleItem] = Field(default_factory=list)


class PipelineRunHistoryItem(BaseModel):
    run_id: str
    week_start: str
    status: str
    started_at: str
    finished_at: str | None
    duration_seconds: int | None
    input_job_ids: list[str]
    config_version: str | None
    error_summary: str | None
    scored_products: int
    top_final_score: float | None
    top_classification: str | None
    report_count: int


class PipelineRunHistoryResponse(BaseModel):
    count: int
    items: list[PipelineRunHistoryItem]


class ReportHistoryItem(BaseModel):
    report_id: str
    run_id: str
    week_start: str
    status: str
    created_at: str
    published_at: str | None
    pipeline_status: str
    report_payload: dict[str, object]
    payload_keys: list[str] = Field(default_factory=list)


class ReportHistoryResponse(BaseModel):
    count: int
    items: list[ReportHistoryItem]


class ContentAngleItem(BaseModel):
    angle_type: str
    hook_text: str
    supporting_rationale: str | None = None
    week_start: str


class ContentAnglesResponse(BaseModel):
    product_id: str
    count: int
    angles: list[ContentAngleItem]


class VideoItem(BaseModel):
    video_url: str
    thumbnail_url: str | None = None
    title: str | None = None
    views: int | None = None


class ProductVideosResponse(BaseModel):
    product_id: str
    videos: list[VideoItem]
    source: str
