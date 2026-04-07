"""Pydantic models for the standalone offline ranking package."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RankingEntry(BaseModel):
    """One ranked product entry in an offline ranking report."""

    model_config = ConfigDict(extra="forbid")

    rank: int = Field(ge=1)
    product_id: str
    name: str
    category: str
    final_score: float = Field(ge=0.0, le=100.0)
    label: str
    trend_score: float = Field(ge=0.0, le=100.0)
    revenue_score: float = Field(ge=0.0, le=100.0)
    competition_score: float = Field(ge=0.0, le=100.0)
    viral_score: float = Field(ge=0.0, le=100.0)
    decay_factor: float = Field(ge=0.0)
    acceleration_bonus: float = Field(ge=1.0)
    estimated_weekly_commission: float = Field(ge=0.0)
    days_since_detected: int = Field(ge=0)
    scored_at: datetime


class RankingReport(BaseModel):
    """Full offline ranking report generated from a batch of product signals."""

    model_config = ConfigDict(extra="forbid")

    report_id: str
    generated_at: datetime
    week_label: str
    total_products_analyzed: int = Field(ge=0)
    top_n: int = Field(ge=0)
    filters_applied: dict[str, object]
    params_used: dict[str, object]
    entries: list[RankingEntry]
