"""LLM-backed saturation estimator built on top of the deterministic SIR model."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from scoring.saturation_model import estimate_opportunity_window, simulate_sir
from services.agents.prompts.saturation_params import SATURATION_PARAMS_PROMPT
from services.shared.db.models import CreatorProduct, Product, ProductScore
from services.shared.llm_client import LLM_AVAILABLE, llm_json_call

logger = logging.getLogger(__name__)

SATURATION_AGENT_NAME = "saturation"

_LLM_CACHE: dict[str, dict[str, object]] = {}

_CATEGORY_NICHE_HINTS = {
    "beauty": 80,
    "home": 70,
    "kitchen": 65,
    "fashion": 60,
    "tech": 50,
}


@dataclass(frozen=True, slots=True)
class SaturationEstimate:
    product_id: str
    beta: float
    gamma: float
    niche_size: int
    current_creators: int
    opportunity_window_days: int | None
    trajectory: list[dict[str, float | int | str]]
    evidence: dict[str, object]

    def as_payload(self) -> dict[str, object]:
        return {
            "product_id": self.product_id,
            "beta": self.beta,
            "gamma": self.gamma,
            "niche_size": self.niche_size,
            "current_creators": self.current_creators,
            "opportunity_window_days": self.opportunity_window_days,
            "trajectory": list(self.trajectory),
            "evidence": dict(self.evidence),
        }


def _llm_cache_key(*, product_id: str) -> str:
    return f"{product_id}:{date.today().isoformat()}"


def _clamp_float(value: object, *, lower: float, upper: float, default: float) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = default
    return max(lower, min(upper, numeric))


def _context_string(
    *, category: str | None, classification: str | None, lifecycle_phase: str | None
) -> str:
    return (
        f"category={category or 'unknown'}; "
        f"classification={classification or 'unknown'}; "
        f"lifecycle_phase={lifecycle_phase or 'unknown'}"
    )


def _niche_size_hint(category: str | None, current_creators: int) -> int:
    category_key = (category or "").lower()
    category_hint = _CATEGORY_NICHE_HINTS.get(category_key, 75)
    creator_floor = max(20, current_creators * 5)
    return max(category_hint, creator_floor)


def _creator_count(session: Session, *, product_id: str, fallback: int) -> int:
    creator_count = session.execute(
        select(func.count(CreatorProduct.id)).where(CreatorProduct.product_id == product_id)
    ).scalar_one()
    if isinstance(creator_count, int) and creator_count > 0:
        return creator_count
    return fallback


def _seed_from_score(score: ProductScore) -> dict[str, object]:
    payload = score.explainability_payload or {}
    return {
        "product_id": score.product_id,
        "title": payload.get("product_title"),
        "category": payload.get("category"),
        "classification": score.classification,
        "lifecycle_phase": score.lifecycle_phase,
        "trend_score": float(score.trend_score or 0.0),
        "creator_accessibility_score": float(score.creator_accessibility_score or 0.0),
    }


def _normalize_llm_payload(payload: dict[str, object]) -> dict[str, object]:
    return {
        "beta": _clamp_float(payload.get("beta"), lower=0.0, upper=1.0, default=0.15),
        "gamma": _clamp_float(payload.get("gamma"), lower=0.0, upper=1.0, default=0.05),
        "reasoning": str(payload.get("reasoning") or ""),
    }


async def _evaluate_with_llm(agent_input: dict[str, object]) -> dict[str, object]:
    prompt = SATURATION_PARAMS_PROMPT.format(
        title=str(agent_input.get("title") or "desconhecido"),
        category=str(agent_input.get("category") or "desconhecida"),
        subcategory=str(agent_input.get("subcategory") or "desconhecida"),
        lifecycle_phase=str(agent_input.get("lifecycle_phase") or "desconhecida"),
        current_creators=int(agent_input.get("current_creators") or 0),
        niche_size=int(agent_input.get("niche_size") or 0),
        context=_context_string(
            category=agent_input.get("category")
            if isinstance(agent_input.get("category"), str)
            else None,
            classification=agent_input.get("classification")
            if isinstance(agent_input.get("classification"), str)
            else None,
            lifecycle_phase=agent_input.get("lifecycle_phase")
            if isinstance(agent_input.get("lifecycle_phase"), str)
            else None,
        ),
    )
    llm_result = await asyncio.to_thread(llm_json_call, prompt)
    if not isinstance(llm_result, dict):
        raise TypeError("llm_json_call returned a non-dict payload")
    return _normalize_llm_payload(llm_result)


def _estimate_parameters(agent_input: dict[str, object]) -> dict[str, object]:
    if not LLM_AVAILABLE:
        return {"beta": 0.15, "gamma": 0.05, "reasoning": "fallback_heuristic"}

    cache_key = _llm_cache_key(product_id=str(agent_input["product_id"]))
    cached = _LLM_CACHE.get(cache_key)
    if cached is not None:
        logger.debug("saturation_agent cache hit for %s", cache_key)
        return cached

    try:
        llm_payload = asyncio.run(_evaluate_with_llm(agent_input))
        _LLM_CACHE[cache_key] = llm_payload
        return llm_payload
    except Exception as exc:
        logger.warning("saturation_agent LLM fallback for %s: %s", agent_input["product_id"], exc)
        return {"beta": 0.15, "gamma": 0.05, "reasoning": "fallback_heuristic"}


def estimate_saturation_for_product(
    session: Session,
    *,
    score: ProductScore,
    week_start: date,
    days_ahead: int = 30,
) -> SaturationEstimate:
    product = session.get(Product, score.product_id)
    if product is None:
        raise RuntimeError(f"Product `{score.product_id}` was not found for saturation estimate.")

    current_creators = _creator_count(
        session,
        product_id=product.id,
        fallback=max(1, int(round(float(score.creator_accessibility_score or 0.0) / 20.0))),
    )
    niche_size = _niche_size_hint(product.category, current_creators)
    agent_input: dict[str, object] = {
        "product_id": product.id,
        "title": product.title,
        "category": product.category,
        "subcategory": product.subcategory,
        "classification": score.classification,
        "lifecycle_phase": score.lifecycle_phase,
        "current_creators": current_creators,
        "niche_size": niche_size,
        "week_start": week_start.isoformat(),
    }
    params = _estimate_parameters(agent_input)
    beta = float(params.get("beta", 0.15))
    gamma = float(params.get("gamma", 0.05))
    trajectory = simulate_sir(current_creators, niche_size, beta, gamma, days_ahead=days_ahead)
    opportunity_window = estimate_opportunity_window(trajectory)

    return SaturationEstimate(
        product_id=product.id,
        beta=beta,
        gamma=gamma,
        niche_size=niche_size,
        current_creators=current_creators,
        opportunity_window_days=opportunity_window,
        trajectory=trajectory,
        evidence={
            "agent_name": SATURATION_AGENT_NAME,
            "week_start": week_start.isoformat(),
            "product_id": product.id,
            "title": product.title,
            "category": product.category,
            "classification": score.classification,
            "lifecycle_phase": score.lifecycle_phase,
            "beta": beta,
            "gamma": gamma,
            "current_creators": current_creators,
            "niche_size": niche_size,
            "reasoning": params.get("reasoning", ""),
        },
    )


def estimate_saturation_for_top_products(
    session: Session,
    *,
    run_id: str,
    week_start: date,
    limit: int = 50,
) -> list[SaturationEstimate]:
    rows = (
        session.execute(
            select(ProductScore)
            .where(ProductScore.run_id == run_id)
            .order_by(ProductScore.final_score.desc(), ProductScore.product_id)
            .limit(limit)
        )
        .scalars()
        .all()
    )
    if not rows:
        logger.info("No product scores were available for saturation estimation.")
        return []

    estimates: list[SaturationEstimate] = []
    for score in rows:
        estimate = estimate_saturation_for_product(session, score=score, week_start=week_start)
        payload = dict(score.explainability_payload or {})
        payload["saturation_model"] = estimate.as_payload()
        payload["opportunity_window_days"] = estimate.opportunity_window_days
        score.explainability_payload = payload
        estimates.append(estimate)

    logger.info("Estimated saturation for %d products in run %s.", len(estimates), run_id)
    return estimates
