from datetime import UTC, date, datetime
from decimal import Decimal
from typing import cast

from services.agents import AgentScoreInput, evaluate_trend_input


def test_trend_agent_returns_structured_score_and_reasoning() -> None:
    agent_input = AgentScoreInput(
        product_id="product-1",
        product_title="Portable Blender Cup",
        brand="BlendGo",
        category="Kitchen",
        subcategory="Drinkware",
        image_url="https://example.com/blender-cup.jpg",
        week_start=date(2026, 3, 9),
        snapshot_count=2,
        latest_observed_at=datetime(2026, 3, 13, 10, 0, tzinfo=UTC),
        signal_values={
            "orders_estimate_current": Decimal("180"),
            "revenue_proxy_current": Decimal("5382.00"),
            "rating_current": Decimal("4.70"),
        },
    )

    result = evaluate_trend_input(agent_input)
    payload = result.as_payload()
    reasoning_payload = cast(dict[str, object], payload["reasoning"])
    breakdown_payload = cast(dict[str, int], reasoning_payload["signal_breakdown"])
    strengths_payload = cast(list[str], reasoning_payload["strengths"])
    risk_flags_payload = cast(list[str], reasoning_payload["risk_flags"])

    assert result.agent_name == "trend"
    assert result.normalized_score == 83
    assert payload["week_start"] == "2026-03-09"
    assert breakdown_payload["orders_velocity"] == 36
    assert breakdown_payload["signal_persistence"] == 20
    assert "strong demand proxy" in strengths_payload[0].lower()
    assert risk_flags_payload == []


def test_trend_agent_flags_weak_evidence_and_missing_category() -> None:
    agent_input = AgentScoreInput(
        product_id="product-2",
        product_title="Mystery Organizer Bin",
        brand=None,
        category=None,
        subcategory="Storage",
        image_url=None,
        week_start=date(2026, 3, 9),
        snapshot_count=1,
        latest_observed_at=None,
        signal_values={
            "orders_estimate_current": Decimal("40"),
            "revenue_proxy_current": Decimal("0"),
        },
    )

    result = evaluate_trend_input(agent_input)

    assert result.normalized_score == 18
    assert "weak_evidence" in result.reasoning.risk_flags
    assert "category_noise" in result.reasoning.risk_flags
    assert len(result.reasoning.weaknesses) >= 2
