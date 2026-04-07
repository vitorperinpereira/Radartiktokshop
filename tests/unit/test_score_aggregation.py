from datetime import UTC, date, datetime
from decimal import Decimal

import services.agents.runtime.creator_accessibility_agent as creator_module
import services.agents.runtime.viral_potential_agent as viral_module
from services.agents import (
    AgentScoreInput,
    evaluate_creator_accessibility_input,
    evaluate_trend_input,
    evaluate_viral_potential_input,
)
from services.scoring import aggregate_score_input, classify_final_score


def test_aggregate_score_input_combines_agent_scores_and_heuristics(
    monkeypatch,
) -> None:
    monkeypatch.setattr(viral_module, "LLM_AVAILABLE", False)
    monkeypatch.setattr(creator_module, "LLM_AVAILABLE", False)
    viral_module._LLM_CACHE.clear()
    creator_module._LLM_CACHE.clear()

    agent_input = AgentScoreInput(
        product_id="product-1",
        product_title="Heatless Curling Ribbon",
        brand="Veloura",
        category="Beauty",
        subcategory="Haircare",
        image_url="https://example.com/curling-ribbon.jpg",
        week_start=date(2026, 3, 9),
        snapshot_count=1,
        latest_observed_at=datetime(2026, 3, 13, 12, 0, tzinfo=UTC),
        signal_values={
            "price_current": Decimal("14.90"),
            "orders_estimate_current": Decimal("320"),
            "rating_current": Decimal("4.80"),
            "commission_rate_current": Decimal("18.00"),
            "revenue_proxy_current": Decimal("4768.00"),
        },
    )

    aggregated_score = aggregate_score_input(
        agent_input=agent_input,
        trend_result=evaluate_trend_input(agent_input).as_payload(),
        viral_result=evaluate_viral_potential_input(agent_input).as_payload(),
        creator_result=evaluate_creator_accessibility_input(agent_input).as_payload(),
        config_version="weekly-bootstrap-v1:smoke",
    )

    assert aggregated_score.trend_score == 81
    assert aggregated_score.viral_potential_score == 79
    assert aggregated_score.creator_accessibility_score == 95
    assert aggregated_score.monetization_score == 90
    assert aggregated_score.saturation_penalty == Decimal("6.00")
    assert aggregated_score.revenue_estimate == Decimal("858.24")
    assert aggregated_score.final_score == Decimal("78.80")
    assert aggregated_score.classification == "strong_weekly_bet"
    assert aggregated_score.explainability_payload["risk_flags"] == ["weak_evidence"]

    explanation = aggregated_score.explainability_payload["explanation"]
    assert isinstance(explanation, dict)
    assert explanation["summary"] == aggregated_score.explainability_payload["summary"]
    assert len(explanation["strengths"]) >= 1
    assert len(explanation["weaknesses"]) >= 1
    assert len(explanation["evidence"]) >= 3


def test_classify_final_score_maps_expected_bands() -> None:
    assert classify_final_score(Decimal("85.00")) == "breakout_candidate"
    assert classify_final_score(Decimal("84.99")) == "strong_weekly_bet"
    assert classify_final_score(Decimal("70.00")) == "strong_weekly_bet"
    assert classify_final_score(Decimal("69.99")) == "test_selectively"
    assert classify_final_score(Decimal("55.00")) == "test_selectively"
    assert classify_final_score(Decimal("54.99")) == "watchlist_only"
    assert classify_final_score(Decimal("40.00")) == "watchlist_only"
    assert classify_final_score(Decimal("39.99")) == "low_priority"
