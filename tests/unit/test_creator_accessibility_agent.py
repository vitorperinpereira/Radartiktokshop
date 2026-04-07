from datetime import UTC, date, datetime
from decimal import Decimal

import services.agents.runtime.creator_accessibility_agent as creator_module
from services.agents import AgentScoreInput, evaluate_creator_accessibility_input


def test_creator_accessibility_agent_returns_structured_score_and_reasoning(monkeypatch) -> None:
    monkeypatch.setattr(creator_module, "LLM_AVAILABLE", False)
    creator_module._LLM_CACHE.clear()

    agent_input = AgentScoreInput(
        product_id="product-1",
        product_title="Heatless Curling Ribbon",
        brand="Veloura",
        category="Beauty",
        subcategory="Haircare",
        image_url="https://example.com/curling-ribbon.jpg",
        week_start=date(2026, 3, 9),
        snapshot_count=2,
        latest_observed_at=datetime(2026, 3, 13, 10, 0, tzinfo=UTC),
        signal_values={
            "orders_estimate_current": Decimal("320"),
            "price_current": Decimal("14.90"),
        },
    )

    result = evaluate_creator_accessibility_input(agent_input)

    assert result.agent_name == "creator_accessibility"
    assert result.normalized_score == 95
    assert result.reasoning.signal_breakdown["audience_fit"] == 36
    assert result.reasoning.signal_breakdown["price_friction"] == 35
    assert result.reasoning.signal_breakdown["authority_requirement"] == 24
    assert result.reasoning.risk_flags == []


def test_creator_accessibility_agent_flags_high_barrier_for_complex_offer(
    monkeypatch,
) -> None:
    monkeypatch.setattr(creator_module, "LLM_AVAILABLE", False)
    creator_module._LLM_CACHE.clear()

    agent_input = AgentScoreInput(
        product_id="product-2",
        product_title="Professional Smart Therapy Device",
        brand="PostureLab",
        category="Tech",
        subcategory="Wellness",
        image_url="https://example.com/therapy-device.jpg",
        week_start=date(2026, 3, 9),
        snapshot_count=1,
        latest_observed_at=None,
        signal_values={
            "orders_estimate_current": Decimal("40"),
            "price_current": Decimal("89.90"),
        },
    )

    result = evaluate_creator_accessibility_input(agent_input)

    assert result.normalized_score == 24
    assert "weak_evidence" in result.reasoning.risk_flags
    assert "high_creator_barrier" in result.reasoning.risk_flags
    assert len(result.reasoning.weaknesses) >= 2


def test_creator_accessibility_agent_uses_llm_cache_and_clamps_scores(monkeypatch) -> None:
    monkeypatch.setattr(creator_module, "LLM_AVAILABLE", True)
    creator_module._LLM_CACHE.clear()

    calls: list[str] = []

    def fake_llm_json_call(prompt: str, temperature: float = 0.2, max_tokens: int = 400) -> dict:
        calls.append(prompt)
        return {
            "authority_needed": 99,
            "authority_reasoning": "Needs specialists.",
            "audience_fit": -5,
            "audience_reasoning": "Too narrow.",
            "barriers": ["medical authority"],
        }

    monkeypatch.setattr(creator_module, "llm_json_call", fake_llm_json_call)

    agent_input = AgentScoreInput(
        product_id="product-llm",
        product_title="Kit de Microagulhamento Facial",
        brand="SkinLab",
        category="Beauty",
        subcategory="Skincare",
        image_url="https://example.com/kit.jpg",
        week_start=date(2026, 3, 9),
        snapshot_count=3,
        latest_observed_at=datetime(2026, 3, 13, 10, 0, tzinfo=UTC),
        signal_values={
            "orders_estimate_current": Decimal("120"),
            "price_current": Decimal("64.90"),
        },
    )

    first_result = creator_module.evaluate_creator_accessibility_input(agent_input)
    second_result = creator_module.evaluate_creator_accessibility_input(agent_input)

    assert first_result.reasoning.signal_breakdown["authority_requirement"] == 25
    assert first_result.reasoning.signal_breakdown["audience_fit"] == 0
    assert first_result.reasoning.evidence[-1].startswith("llm_result=")
    assert first_result.normalized_score == second_result.normalized_score
    assert len(calls) == 1
