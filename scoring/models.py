"""Pydantic models for the standalone deterministic scoring engine."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductSignals(BaseModel):
    """Normalized raw inputs required to score one TikTok Shop product."""

    model_config = ConfigDict(extra="forbid")

    product_id: str
    name: str
    category: str
    price: float = Field(ge=0.0)
    commission_rate: float = Field(ge=0.0)
    sales_velocity: float = Field(ge=0.0)
    google_trend_score: float = Field(default=0.0, ge=0.0, le=100.0)
    view_growth_7d: float = Field(ge=0.0)
    view_growth_3d: float = Field(ge=0.0)
    active_creators: int = Field(ge=0)
    days_since_detected: int = Field(ge=0)
    demo_value: float = Field(ge=0.0, le=100.0)
    visual_transform: float = Field(ge=0.0, le=100.0)
    hook_clarity: float = Field(ge=0.0, le=100.0)


class ProductScore(BaseModel):
    """Final scoring output for one product under the standalone engine."""

    model_config = ConfigDict(extra="forbid")

    product_id: str
    name: str
    final_score: float = Field(ge=0.0, le=100.0)
    base_score: float = Field(ge=0.0, le=100.0)
    trend_score: float = Field(ge=0.0, le=100.0)
    revenue_score: float = Field(ge=0.0, le=100.0)
    price_score: float = Field(ge=0.0, le=100.0)
    opportunity_score: float = Field(ge=0.0, le=100.0)
    lifecycle_phase: str
    viral_score: float = Field(ge=0.0, le=100.0)
    decay_factor: float = Field(ge=0.0)
    acceleration_bonus: float = Field(ge=1.0)
    label: str
    scored_at: datetime

    @property
    def competition_score(self) -> float:
        return self.opportunity_score
