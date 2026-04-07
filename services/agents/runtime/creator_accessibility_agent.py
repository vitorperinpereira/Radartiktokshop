"""Creator Accessibility Agent runtime with LLM fallback and deterministic price friction."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from services.agents.contracts import AgentReasoning, AgentScoreInput, AgentScoreResult
from services.agents.prompts.accessibility_assessment import ACCESSIBILITY_PROMPT
from services.agents.runtime.trend_agent import load_trend_inputs
from services.shared.llm_client import LLM_AVAILABLE, llm_json_call

logger = logging.getLogger(__name__)

CREATOR_ACCESSIBILITY_AGENT_NAME = "creator_accessibility"

_LLM_CACHE: dict[str, dict[str, object]] = {}

_ACCESSIBLE_CATEGORIES = {
    "beauty": 34,
    "home": 32,
    "kitchen": 31,
    "fashion": 30,
    "tech": 18,
}
_ACCESSIBLE_SUBCATEGORIES = {
    "haircare": 34,
    "cleaning": 32,
    "decor": 30,
    "drinkware": 30,
    "storage": 28,
}
_AUTHORITY_BASE_BY_CATEGORY = {
    "beauty": 22,
    "home": 24,
    "kitchen": 24,
    "fashion": 22,
    "tech": 14,
}
_AUTHORITY_RISK_KEYWORDS = {
    "advanced",
    "clinical",
    "expert",
    "professional",
    "pro",
    "premium",
    "smart",
    "therapy",
}
_LOW_BARRIER_KEYWORDS = {
    "heatless",
    "mini",
    "pet",
    "portable",
}


def load_creator_accessibility_inputs(
    session: Session, *, week_start: date
) -> list[AgentScoreInput]:
    return load_trend_inputs(session, week_start=week_start)


def _tokenize(agent_input: AgentScoreInput) -> set[str]:
    title_tokens = agent_input.product_title.lower().replace("-", " ").split()
    subcategory_tokens = (agent_input.subcategory or "").lower().replace("-", " ").split()
    return {token for token in [*title_tokens, *subcategory_tokens] if token}


def _low_barrier_seed(agent_input: AgentScoreInput) -> int:
    category_key = (agent_input.category or "").lower()
    if category_key:
        return _ACCESSIBLE_CATEGORIES.get(category_key, 24)

    subcategory_key = (agent_input.subcategory or "").lower()
    if subcategory_key:
        return _ACCESSIBLE_SUBCATEGORIES.get(subcategory_key, 24)

    return 24


def _price_component(price: Decimal | None) -> int:
    if price is None:
        return 12
    if Decimal("8") <= price <= Decimal("30"):
        return 35
    if price <= Decimal("45"):
        return 26
    if price <= Decimal("70"):
        return 16
    return 6


def _authority_component(agent_input: AgentScoreInput, tokens: set[str]) -> int:
    category_key = (agent_input.category or "").lower()
    base = _AUTHORITY_BASE_BY_CATEGORY.get(category_key, 18)
    base += min(4, 2 * sum(token in _LOW_BARRIER_KEYWORDS for token in tokens))
    penalty = 6 * sum(token in _AUTHORITY_RISK_KEYWORDS for token in tokens)
    return max(0, min(25, base - penalty))


def _llm_cache_key(agent_input: AgentScoreInput) -> str:
    return f"{agent_input.product_id}:{date.today().isoformat()}"


def _clamp_int(value: object, upper_bound: int) -> int:
    try:
        numeric = int(round(float(value)))
    except (TypeError, ValueError):
        numeric = 0
    return max(0, min(upper_bound, numeric))


def _normalize_llm_payload(payload: dict[str, object]) -> dict[str, object]:
    barriers = payload.get("barriers")
    return {
        "authority_needed": _clamp_int(payload.get("authority_needed"), 25),
        "authority_reasoning": str(payload.get("authority_reasoning") or ""),
        "audience_fit": _clamp_int(payload.get("audience_fit"), 40),
        "audience_reasoning": str(payload.get("audience_reasoning") or ""),
        "barriers": list(barriers) if isinstance(barriers, list) else [],
    }


def _build_context(agent_input: AgentScoreInput) -> str:
    orders_estimate = agent_input.signal_values.get("orders_estimate_current", "unknown")
    return (
        f"brand={agent_input.brand or 'unknown'}; "
        f"orders_estimate_current={orders_estimate}; "
        f"snapshot_count={agent_input.snapshot_count}; "
        f"title_tokens={sorted(_tokenize(agent_input))}"
    )


async def _evaluate_with_llm(agent_input: AgentScoreInput) -> dict[str, object]:
    prompt = ACCESSIBILITY_PROMPT.format(
        title=agent_input.product_title,
        category=agent_input.category or "desconhecida",
        subcategory=agent_input.subcategory or "desconhecida",
        price=agent_input.signal_values.get("price_current", "N/A"),
        context=_build_context(agent_input),
    )
    llm_result = await asyncio.to_thread(llm_json_call, prompt)
    if not isinstance(llm_result, dict):
        raise TypeError("llm_json_call returned a non-dict payload")
    return _normalize_llm_payload(llm_result)


def _evaluate_with_fallback(
    agent_input: AgentScoreInput,
) -> tuple[int, int, dict[str, object] | None]:
    if not LLM_AVAILABLE:
        tokens = _tokenize(agent_input)
        return (
            _authority_component(agent_input, tokens),
            _low_barrier_seed(agent_input),
            None,
        )

    cache_key = _llm_cache_key(agent_input)
    cached = _LLM_CACHE.get(cache_key)
    if cached is not None:
        logger.debug("creator_accessibility_agent cache hit for %s", cache_key)
        return int(cached["authority_needed"]), int(cached["audience_fit"]), cached

    try:
        llm_payload = asyncio.run(_evaluate_with_llm(agent_input))
        _LLM_CACHE[cache_key] = llm_payload
        return int(llm_payload["authority_needed"]), int(llm_payload["audience_fit"]), llm_payload
    except Exception as exc:
        logger.warning(
            "creator_accessibility_agent LLM fallback for %s: %s",
            agent_input.product_id,
            exc,
        )
        return (
            _authority_component(agent_input, _tokenize(agent_input)),
            _low_barrier_seed(agent_input),
            None,
        )


def evaluate_creator_accessibility_input(agent_input: AgentScoreInput) -> AgentScoreResult:
    authority_component, audience_fit_component, llm_payload = _evaluate_with_fallback(agent_input)
    price = agent_input.signal_values.get("price_current")
    orders = agent_input.signal_values.get("orders_estimate_current", Decimal("0"))

    if llm_payload is None:
        audience_fit_component += min(
            4, 2 * sum(token in _LOW_BARRIER_KEYWORDS for token in _tokenize(agent_input))
        )
        audience_fit_component = min(40, audience_fit_component)

    price_friction_component = _price_component(price)

    signal_breakdown = {
        "audience_fit": audience_fit_component,
        "price_friction": price_friction_component,
        "authority_requirement": authority_component,
    }
    normalized_score = min(100, sum(signal_breakdown.values()))

    strengths: list[str] = []
    weaknesses: list[str] = []
    evidence = [
        f"category={agent_input.category or 'unknown'}",
        f"subcategory={agent_input.subcategory or 'unknown'}",
        f"title_keywords={sorted(_tokenize(agent_input))}",
        f"snapshot_count={agent_input.snapshot_count}",
        f"orders_estimate_current={int(orders)}",
    ]
    if price is not None:
        evidence.append(f"price_current={price.quantize(Decimal('0.01'))}")

    if llm_payload is not None:
        evidence.append(f"llm_result={json.dumps(llm_payload, ensure_ascii=False, sort_keys=True)}")
    else:
        evidence.append("llm_result=fallback_heuristic")

    if audience_fit_component >= 30:
        strengths.append("Product category and framing look accessible for a broad creator base.")
    if price_friction_component >= 26:
        strengths.append("Price point keeps buyer friction low for smaller creator campaigns.")
    if authority_component >= 18:
        strengths.append("Offer does not appear to demand strong authority or niche expertise.")

    risk_flags: list[str] = []
    if agent_input.snapshot_count < 2:
        weaknesses.append(
            "Only one recent snapshot is available, reducing confidence in accessibility."
        )
        risk_flags.append("weak_evidence")
    if agent_input.category is None:
        weaknesses.append("Missing category metadata makes creator-fit framing less reliable.")
        risk_flags.append("category_noise")
    if price_friction_component <= 16:
        weaknesses.append(
            "Price point adds friction for smaller creators trying to convert impulse buys."
        )
    if authority_component <= 12:
        weaknesses.append(
            "Product likely needs stronger authority, explanation, or niche trust to sell."
        )
    if normalized_score < 45:
        risk_flags.append("high_creator_barrier")

    if not strengths:
        strengths.append(
            "The product is still testable, but creator fit needs tighter positioning."
        )

    summary = (
        f"Creator accessibility score {normalized_score} for {agent_input.product_title} is driven "
        "by audience breadth, buyer friction from price, and the amount of authority likely "
        "needed for a smaller creator to sell it."
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
        agent_name=CREATOR_ACCESSIBILITY_AGENT_NAME,
        product_id=agent_input.product_id,
        week_start=agent_input.week_start,
        normalized_score=normalized_score,
        reasoning=reasoning,
    )


def evaluate_creator_accessibility_candidates(
    session: Session, week_start: date
) -> list[AgentScoreResult]:
    return [
        evaluate_creator_accessibility_input(agent_input)
        for agent_input in load_creator_accessibility_inputs(session, week_start=week_start)
    ]
