"""Shared scoring contracts for MVP runtime agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True)
class AgentReasoning:
    summary: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    signal_breakdown: dict[str, int] = field(default_factory=dict)

    def as_payload(self) -> dict[str, object]:
        return {
            "summary": self.summary,
            "strengths": list(self.strengths),
            "weaknesses": list(self.weaknesses),
            "evidence": list(self.evidence),
            "risk_flags": list(self.risk_flags),
            "signal_breakdown": dict(self.signal_breakdown),
        }


@dataclass(frozen=True)
class AgentScoreInput:
    product_id: str
    product_title: str
    brand: str | None
    category: str | None
    subcategory: str | None
    image_url: str | None
    week_start: date
    snapshot_count: int
    latest_observed_at: datetime | None
    signal_values: dict[str, Decimal]

    def as_payload(self) -> dict[str, object]:
        return {
            "product_id": self.product_id,
            "product_title": self.product_title,
            "brand": self.brand,
            "category": self.category,
            "subcategory": self.subcategory,
            "image_url": self.image_url,
            "week_start": self.week_start.isoformat(),
            "snapshot_count": self.snapshot_count,
            "latest_observed_at": (
                None if self.latest_observed_at is None else self.latest_observed_at.isoformat()
            ),
            "signal_values": {
                name: str(value) for name, value in sorted(self.signal_values.items())
            },
        }


@dataclass(frozen=True)
class AgentScoreResult:
    agent_name: str
    product_id: str
    week_start: date
    normalized_score: int
    reasoning: AgentReasoning

    def as_payload(self) -> dict[str, object]:
        return {
            "agent_name": self.agent_name,
            "product_id": self.product_id,
            "week_start": self.week_start.isoformat(),
            "normalized_score": self.normalized_score,
            "reasoning": self.reasoning.as_payload(),
        }
