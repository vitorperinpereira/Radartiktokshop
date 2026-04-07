"""Viral Potential Agent runtime with LLM fallback and deterministic shareability."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from services.agents.contracts import AgentReasoning, AgentScoreInput, AgentScoreResult
from services.agents.prompts.viral_assessment import VIRAL_ASSESSMENT_PROMPT
from services.agents.runtime.trend_agent import load_trend_inputs
from services.shared.llm_client import LLM_AVAILABLE, llm_json_call

logger = logging.getLogger(__name__)

VIRAL_POTENTIAL_AGENT_NAME = "viral_potential"

_LLM_CACHE: dict[str, dict[str, object]] = {}

_VISUAL_CATEGORIES = {
    "beauty": 30,
    "home": 26,
    "kitchen": 25,
    "fashion": 22,
    "tech": 20,
}
_SUBCATEGORY_VISUAL_HINTS = {
    "storage": 22,
    "organization": 22,
    "haircare": 30,
    "kitchen gadgets": 25,
    "pet supplies": 24,
}
_VISUAL_KEYWORDS = {
    "blender",
    "lamp",
    "roller",
    "curling",
    "heatless",
    "vacuum",
    "led",
    "pet",
}
_HOOK_KEYWORDS = {
    "portable",
    "mini",
    "heatless",
    "pet",
    "led",
    "sunset",
    "roller",
    "blender",
    "vacuum",
    "curling",
}


def load_viral_potential_inputs(session: Session, *, week_start: date) -> list[AgentScoreInput]:
    return load_trend_inputs(session, week_start=week_start)


def _tokenize_title(agent_input: AgentScoreInput) -> set[str]:
    return {token for token in agent_input.product_title.lower().replace("-", " ").split() if token}


def _resolve_visual_component_seed(agent_input: AgentScoreInput) -> int:
    category_key = (agent_input.category or "").lower()
    if category_key:
        return _VISUAL_CATEGORIES.get(category_key, 18)

    subcategory_key = (agent_input.subcategory or "").lower()
    if subcategory_key:
        return _SUBCATEGORY_VISUAL_HINTS.get(subcategory_key, 18)

    return 18


def _compute_visual_component(agent_input: AgentScoreInput) -> int:
    title_tokens = _tokenize_title(agent_input)
    visual_component = _resolve_visual_component_seed(agent_input)
    visual_component += min(10, 5 * sum(token in _VISUAL_KEYWORDS for token in title_tokens))
    return min(40, visual_component)


def _compute_hook_component(agent_input: AgentScoreInput) -> int:
    title_tokens = _tokenize_title(agent_input)
    return min(35, 7 * sum(token in _HOOK_KEYWORDS for token in title_tokens))


def _compute_shareability_component(agent_input: AgentScoreInput) -> int:
    orders = agent_input.signal_values.get("orders_estimate_current", Decimal("0"))
    price = agent_input.signal_values.get("price_current")
    shareability_component = min(15, int(orders / Decimal("20")))
    if price is not None:
        if Decimal("8") <= price <= Decimal("35"):
            shareability_component += 10
        elif price <= Decimal("50"):
            shareability_component += 6
        else:
            shareability_component += 2
    return min(25, shareability_component)


def _llm_cache_key(agent_input: AgentScoreInput) -> str:
    return f"{agent_input.product_id}:{date.today().isoformat()}"


def _format_price(price: Decimal | None) -> str:
    if price is None:
        return "N/A"
    return f"{price.quantize(Decimal('0.01'))}"


def _build_description_snippet(agent_input: AgentScoreInput) -> str:
    orders = agent_input.signal_values.get("orders_estimate_current")
    price = agent_input.signal_values.get("price_current")
    return (
        f"brand={agent_input.brand or 'unknown'}; "
        f"category={agent_input.category or 'unknown'}; "
        f"subcategory={agent_input.subcategory or 'unknown'}; "
        f"snapshot_count={agent_input.snapshot_count}; "
        f"orders_estimate_current={orders if orders is not None else 'unknown'}; "
        f"price_current={_format_price(price)}"
    )


def _clamp_int(value: object, upper_bound: int) -> int:
    try:
        numeric = int(round(float(value)))
    except (TypeError, ValueError):
        numeric = 0
    return max(0, min(upper_bound, numeric))


def _normalize_llm_payload(payload: dict[str, object]) -> dict[str, object]:
    return {
        "visual_demo_score": _clamp_int(payload.get("visual_demo_score"), 40),
        "visual_reasoning": str(payload.get("visual_reasoning") or ""),
        "hook_score": _clamp_int(payload.get("hook_score"), 35),
        "hook_reasoning": str(payload.get("hook_reasoning") or ""),
        "suggested_format": str(payload.get("suggested_format") or "review"),
        "confidence": max(0.0, min(1.0, float(payload.get("confidence") or 0.0))),
    }


async def _evaluate_with_llm(agent_input: AgentScoreInput) -> dict[str, object]:
    prompt = VIRAL_ASSESSMENT_PROMPT.format(
        title=agent_input.product_title,
        category=agent_input.category or "desconhecida",
        subcategory=agent_input.subcategory or "desconhecida",
        price=_format_price(agent_input.signal_values.get("price_current")),
        description_snippet=_build_description_snippet(agent_input),
    )
    llm_result = await asyncio.to_thread(llm_json_call, prompt)
    if not isinstance(llm_result, dict):
        raise TypeError("llm_json_call returned a non-dict payload")
    normalized = _normalize_llm_payload(llm_result)
    return normalized


def _evaluate_with_fallback(
    agent_input: AgentScoreInput,
) -> tuple[int, int, dict[str, object] | None]:
    if not LLM_AVAILABLE:
        return _compute_visual_component(agent_input), _compute_hook_component(agent_input), None

    cache_key = _llm_cache_key(agent_input)
    cached = _LLM_CACHE.get(cache_key)
    if cached is not None:
        logger.debug("viral_potential_agent cache hit for %s", cache_key)
        return int(cached["visual_demo_score"]), int(cached["hook_score"]), cached

    try:
        llm_payload = asyncio.run(_evaluate_with_llm(agent_input))
        _LLM_CACHE[cache_key] = llm_payload
        return int(llm_payload["visual_demo_score"]), int(llm_payload["hook_score"]), llm_payload
    except Exception as exc:
        logger.warning("viral_potential_agent LLM fallback for %s: %s", agent_input.product_id, exc)
        return _compute_visual_component(agent_input), _compute_hook_component(agent_input), None


def evaluate_viral_potential_input(agent_input: AgentScoreInput) -> AgentScoreResult:
    visual_component, hook_component, llm_payload = _evaluate_with_fallback(agent_input)
    shareability_component = _compute_shareability_component(agent_input)

    signal_breakdown = {
        "visual_demo_potential": visual_component,
        "hook_strength": hook_component,
        "shareability": shareability_component,
    }
    normalized_score = min(100, sum(signal_breakdown.values()))

    strengths: list[str] = []
    weaknesses: list[str] = []
    evidence = [
        f"category={agent_input.category or 'unknown'}",
        f"title_keywords={sorted(_tokenize_title(agent_input))}",
        f"snapshot_count={agent_input.snapshot_count}",
    ]
    if agent_input.signal_values.get("price_current") is not None:
        evidence.append(
            f"price_current={_format_price(agent_input.signal_values.get('price_current'))}"
        )
    orders_estimate_current = int(
        agent_input.signal_values.get("orders_estimate_current", Decimal("0"))
    )
    evidence.append(f"orders_estimate_current={orders_estimate_current}")

    if llm_payload is not None:
        evidence.append(f"llm_result={json.dumps(llm_payload, ensure_ascii=False, sort_keys=True)}")
    else:
        evidence.append("llm_result=fallback_heuristic")

    if visual_component >= 30:
        strengths.append("Product has strong visual demo potential for short-form content.")
    if hook_component >= 21:
        strengths.append("Title contains hook-friendly keywords that can support strong opens.")
    if shareability_component >= 18:
        strengths.append("Price and demand proxy support easy sharing and impulse interest.")

    risk_flags: list[str] = []
    if agent_input.snapshot_count < 2:
        weaknesses.append(
            "Only one recent snapshot is available, reducing confidence in repeated appeal."
        )
        risk_flags.append("weak_evidence")
    if agent_input.category is None:
        weaknesses.append("Missing category metadata makes viral framing less reliable.")
        risk_flags.append("category_noise")
    if hook_component == 0:
        weaknesses.append("Title lacks obvious hook keywords for short-form content.")
    if agent_input.image_url is None:
        weaknesses.append("No image asset is available to validate demo readiness.")

    if not strengths:
        strengths.append("The product still has enough structure to test short-form positioning.")

    summary = (
        f"Viral potential score {normalized_score} for {agent_input.product_title} is driven by "
        f"visual demo fit, hook-ready naming, and shareability proxies from price and demand."
    )

    reasoning = AgentReasoning(
        summary=summary,
        strengths=strengths,
        weaknesses=weaknesses,
        evidence=evidence,
        risk_flags=risk_flags,
        signal_breakdown=signal_breakdown,
    )
    return AgentScoreResult(
        agent_name=VIRAL_POTENTIAL_AGENT_NAME,
        product_id=agent_input.product_id,
        week_start=agent_input.week_start,
        normalized_score=normalized_score,
        reasoning=reasoning,
    )


def evaluate_viral_potential_candidates(
    session: Session, week_start: date
) -> list[AgentScoreResult]:
    return [
        evaluate_viral_potential_input(agent_input)
        for agent_input in load_viral_potential_inputs(session, week_start=week_start)
    ]
