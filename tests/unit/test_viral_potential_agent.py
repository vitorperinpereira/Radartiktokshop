from datetime import UTC, date, datetime
from decimal import Decimal

import services.agents.runtime.viral_potential_agent as viral_module
from services.agents import AgentScoreInput, evaluate_viral_potential_input


def test_viral_potential_agent_returns_structured_score_and_reasoning(monkeypatch) -> None:
    monkeypatch.setattr(viral_module, "LLM_AVAILABLE", False)
    viral_module._LLM_CACHE.clear()

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

    result = evaluate_viral_potential_input(agent_input)

    assert result.agent_name == "viral_potential"
    assert result.normalized_score == 79
    assert result.reasoning.signal_breakdown["visual_demo_potential"] == 40
    assert result.reasoning.signal_breakdown["hook_strength"] == 14
    assert result.reasoning.signal_breakdown["shareability"] == 25
    assert result.reasoning.risk_flags == []


def test_viral_potential_agent_flags_weak_evidence_when_assets_are_missing(
    monkeypatch,
) -> None:
    monkeypatch.setattr(viral_module, "LLM_AVAILABLE", False)
    viral_module._LLM_CACHE.clear()

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
            "price_current": Decimal("59.90"),
        },
    )

    result = evaluate_viral_potential_input(agent_input)

    assert result.normalized_score == 26
    assert "weak_evidence" in result.reasoning.risk_flags
    assert "category_noise" in result.reasoning.risk_flags
    assert len(result.reasoning.weaknesses) >= 2


def test_viral_potential_agent_uses_llm_cache_and_clamps_scores(monkeypatch) -> None:
    monkeypatch.setattr(viral_module, "LLM_AVAILABLE", True)
    viral_module._LLM_CACHE.clear()

    calls: list[str] = []

    def fake_llm_json_call(prompt: str, temperature: float = 0.2, max_tokens: int = 400) -> dict:
        calls.append(prompt)
        return {
            "visual_demo_score": 99,
            "visual_reasoning": "Highly visual.",
            "hook_score": -5,
            "hook_reasoning": "Needs context.",
            "suggested_format": "before_after",
            "confidence": 1.5,
        }

    monkeypatch.setattr(viral_module, "llm_json_call", fake_llm_json_call)

    agent_input = AgentScoreInput(
        product_id="product-llm",
        product_title="Escova Alisadora Ceramica",
        brand="Veloura",
        category="Beauty",
        subcategory="Haircare",
        image_url="https://example.com/brush.jpg",
        week_start=date(2026, 3, 9),
        snapshot_count=3,
        latest_observed_at=datetime(2026, 3, 13, 10, 0, tzinfo=UTC),
        signal_values={
            "orders_estimate_current": Decimal("320"),
            "price_current": Decimal("14.90"),
        },
    )

    first_result = viral_module.evaluate_viral_potential_input(agent_input)
    second_result = viral_module.evaluate_viral_potential_input(agent_input)

    assert first_result.reasoning.signal_breakdown["visual_demo_potential"] == 40
    assert first_result.reasoning.signal_breakdown["hook_strength"] == 0
    assert first_result.reasoning.evidence[-1].startswith("llm_result=")
    assert first_result.normalized_score == second_result.normalized_score
    assert len(calls) == 1
