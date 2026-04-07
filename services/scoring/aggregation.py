"""Deterministic final score aggregation and persistence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.agents.contracts import AgentScoreInput
from services.shared.db.models import ProductScore

SCORE_POLICY_VERSION = "score-mvp-v1"

_ZERO = Decimal("0")
_TWO_PLACES = Decimal("0.01")
_WEIGHTS = {
    "trend": Decimal("0.35"),
    "viral_potential": Decimal("0.30"),
    "creator_accessibility": Decimal("0.25"),
    "monetization": Decimal("0.10"),
}


@dataclass(frozen=True)
class AggregatedProductScore:
    product_id: str
    week_start: date
    trend_score: int
    viral_potential_score: int
    creator_accessibility_score: int
    monetization_score: int
    saturation_penalty: Decimal
    revenue_estimate: Decimal
    final_score: Decimal
    classification: str
    lifecycle_phase: str
    explainability_payload: dict[str, object]


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)


def classify_final_score(final_score: Decimal) -> str:
    if final_score >= Decimal("85"):
        return "breakout_candidate"
    if final_score >= Decimal("70"):
        return "strong_weekly_bet"
    if final_score >= Decimal("55"):
        return "test_selectively"
    if final_score >= Decimal("40"):
        return "watchlist_only"
    return "low_priority"


def _reasoning_payload(result_payload: dict[str, object]) -> dict[str, object]:
    reasoning = result_payload.get("reasoning")
    if not isinstance(reasoning, dict):
        raise RuntimeError("Agent result payload is missing deterministic reasoning.")
    return reasoning


def _score_value(result_payload: dict[str, object]) -> int:
    raw_value = result_payload.get("normalized_score")
    if not isinstance(raw_value, int):
        raise RuntimeError("Agent result payload is missing a valid normalized_score.")
    return raw_value


def _list_texts(reasoning: dict[str, object], field_name: str) -> list[str]:
    values = reasoning.get(field_name)
    if not isinstance(values, list):
        return []
    return [str(value) for value in values]


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def _price_efficiency_component(price: Decimal | None) -> int:
    if price is None:
        return 10
    if Decimal("8") <= price <= Decimal("35"):
        return 20
    if price <= Decimal("50"):
        return 14
    if price <= Decimal("80"):
        return 8
    return 4


def _monetization_details(agent_input: AgentScoreInput) -> tuple[int, Decimal, dict[str, int]]:
    signal_values = agent_input.signal_values
    price = signal_values.get("price_current")
    orders = signal_values.get("orders_estimate_current", _ZERO)
    commission_rate = signal_values.get("commission_rate_current")

    revenue_estimate = _ZERO
    commission_component = 0
    if commission_rate is not None:
        commission_component = min(40, int(commission_rate * 2))
        if price is not None:
            revenue_estimate = price * orders * commission_rate / Decimal("100")

    revenue_component = min(40, int(revenue_estimate / Decimal("25")))
    price_efficiency_component = _price_efficiency_component(price)
    monetization_score = min(
        100,
        commission_component + revenue_component + price_efficiency_component,
    )
    return (
        monetization_score,
        _quantize(revenue_estimate),
        {
            "commission_rate": commission_component,
            "estimated_commission_value": revenue_component,
            "price_efficiency": price_efficiency_component,
        },
    )


def _google_trends_boost(trend_score: int, agent_input: AgentScoreInput) -> Decimal:
    google_trends_score = agent_input.signal_values.get("google_trends_score")
    if google_trends_score is None:
        return Decimal("1.0")
    if google_trends_score > Decimal("50") and trend_score > 70:
        return Decimal("1.1")
    return Decimal("1.0")


def _lifecycle_phase(trend_score: int, saturation_penalty: Decimal) -> str:
    if saturation_penalty >= Decimal("7.00"):
        return "SATURADO"
    if trend_score >= 85:
        return "PICO"
    if trend_score >= 70:
        return "ACELERANDO"
    return "EMERGENTE"


def _saturation_details(
    agent_input: AgentScoreInput,
    *,
    viral_score: int,
) -> tuple[Decimal, dict[str, int]]:
    orders = agent_input.signal_values.get("orders_estimate_current", _ZERO)
    orders_pressure_component = min(8, int(orders / Decimal("80")))
    repeat_signal_component = min(4, max(0, agent_input.snapshot_count - 1) * 2)
    viral_heat_component = 0
    if viral_score >= 85:
        viral_heat_component = 4
    elif viral_score >= 70:
        viral_heat_component = 2

    saturation_penalty = min(
        15,
        orders_pressure_component + repeat_signal_component + viral_heat_component,
    )
    return (
        _quantize(Decimal(saturation_penalty)),
        {
            "orders_pressure": orders_pressure_component,
            "repeat_signal_pressure": repeat_signal_component,
            "viral_heat": viral_heat_component,
        },
    )


def _build_summary(
    *,
    product_title: str,
    classification: str,
    final_score: Decimal,
    trend_score: int,
    viral_score: int,
    creator_score: int,
    monetization_score: int,
    saturation_penalty: Decimal,
) -> str:
    return (
        f"{product_title} landed in {classification} with final score "
        f"{final_score:.2f}, driven by trend {trend_score}, viral potential "
        f"{viral_score}, creator accessibility {creator_score}, and monetization "
        f"{monetization_score}, offset by saturation penalty {saturation_penalty:.2f}."
    )


def aggregate_score_input(
    *,
    agent_input: AgentScoreInput,
    trend_result: dict[str, object],
    viral_result: dict[str, object],
    creator_result: dict[str, object],
    config_version: str,
) -> AggregatedProductScore:
    trend_score = _score_value(trend_result)
    viral_score = _score_value(viral_result)
    creator_score = _score_value(creator_result)

    monetization_score, revenue_estimate, monetization_breakdown = _monetization_details(
        agent_input
    )
    saturation_penalty, saturation_breakdown = _saturation_details(
        agent_input,
        viral_score=viral_score,
    )

    weighted_total = (
        Decimal(trend_score) * _WEIGHTS["trend"]
        + Decimal(viral_score) * _WEIGHTS["viral_potential"]
        + Decimal(creator_score) * _WEIGHTS["creator_accessibility"]
        + Decimal(monetization_score) * _WEIGHTS["monetization"]
        - saturation_penalty
    )
    trend_boost = _google_trends_boost(trend_score, agent_input)
    final_score = _quantize(max(_ZERO, min(Decimal("100"), weighted_total * trend_boost)))
    classification = classify_final_score(final_score)
    lifecycle_phase = _lifecycle_phase(trend_score, saturation_penalty)

    trend_reasoning = _reasoning_payload(trend_result)
    viral_reasoning = _reasoning_payload(viral_result)
    creator_reasoning = _reasoning_payload(creator_result)

    strengths = _dedupe(
        [
            *_list_texts(trend_reasoning, "strengths"),
            *_list_texts(viral_reasoning, "strengths"),
            *_list_texts(creator_reasoning, "strengths"),
        ]
    )
    weaknesses = _dedupe(
        [
            *_list_texts(trend_reasoning, "weaknesses"),
            *_list_texts(viral_reasoning, "weaknesses"),
            *_list_texts(creator_reasoning, "weaknesses"),
        ]
    )
    evidence = _dedupe(
        [
            *_list_texts(trend_reasoning, "evidence"),
            *_list_texts(viral_reasoning, "evidence"),
            *_list_texts(creator_reasoning, "evidence"),
            f"estimated_commission_value={revenue_estimate:.2f}",
            f"saturation_penalty={saturation_penalty:.2f}",
            f"scoring_config_version={config_version}",
        ]
    )

    heuristic_risk_flags: list[str] = []
    if saturation_penalty >= Decimal("7.00"):
        heuristic_risk_flags.append("high_saturation")
        weaknesses.append("Crowding pressure is elevated based on demand and viral heat.")
    if monetization_score <= 45:
        heuristic_risk_flags.append("low_margin_proxy")
        weaknesses.append("Monetization proxy is weak for the current price and commission mix.")
    if monetization_score >= 70:
        strengths.append("Deterministic monetization proxy supports attractive weekly upside.")

    strengths = _dedupe(strengths)
    weaknesses = _dedupe(weaknesses)
    risk_flags = sorted(
        set(
            [
                *_list_texts(trend_reasoning, "risk_flags"),
                *_list_texts(viral_reasoning, "risk_flags"),
                *_list_texts(creator_reasoning, "risk_flags"),
                *heuristic_risk_flags,
            ]
        )
    )

    if not strengths:
        strengths = ["Signal mix is stable enough to keep the product in the weekly ranking."]
    if not weaknesses:
        weaknesses = ["No major deterministic downside exceeded the current warning thresholds."]

    summary = _build_summary(
        product_title=agent_input.product_title,
        classification=classification,
        final_score=final_score,
        trend_score=trend_score,
        viral_score=viral_score,
        creator_score=creator_score,
        monetization_score=monetization_score,
        saturation_penalty=saturation_penalty,
    )
    explainability_payload = {
        "product_id": agent_input.product_id,
        "week_start": agent_input.week_start.isoformat(),
        "scores": {
            "trend": trend_score,
            "viral_potential": viral_score,
            "creator_accessibility": creator_score,
            "monetization": monetization_score,
            "saturation_penalty": float(saturation_penalty),
            "final": float(final_score),
        },
        "weights": {
            "version": SCORE_POLICY_VERSION,
            "trend": float(_WEIGHTS["trend"]),
            "viral_potential": float(_WEIGHTS["viral_potential"]),
            "creator_accessibility": float(_WEIGHTS["creator_accessibility"]),
            "monetization": float(_WEIGHTS["monetization"]),
        },
        "classification": classification,
        "lifecycle_phase": lifecycle_phase,
        "risk_flags": risk_flags,
        "summary": summary,
        "top_positive_signals": strengths[:3],
        "top_negative_signals": weaknesses[:3],
        "applied_penalties": {
            "saturation_penalty": float(saturation_penalty),
        },
        "revenue_estimate": float(revenue_estimate),
        "heuristics": {
            "monetization": monetization_breakdown,
            "saturation": saturation_breakdown,
            "google_trends_boost": float(trend_boost),
        },
        "explanation": {
            "summary": summary,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "evidence": evidence,
        },
        "agent_reasoning": {
            "trend": trend_reasoning,
            "viral_potential": viral_reasoning,
            "creator_accessibility": creator_reasoning,
        },
    }
    return AggregatedProductScore(
        product_id=agent_input.product_id,
        week_start=agent_input.week_start,
        trend_score=trend_score,
        viral_potential_score=viral_score,
        creator_accessibility_score=creator_score,
        monetization_score=monetization_score,
        saturation_penalty=saturation_penalty,
        revenue_estimate=revenue_estimate,
        final_score=final_score,
        classification=classification,
        lifecycle_phase=lifecycle_phase,
        explainability_payload=explainability_payload,
    )


def _result_index(result_payloads: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {str(payload["product_id"]): payload for payload in result_payloads}


def _upsert_product_score(
    session: Session,
    *,
    run_id: str,
    aggregated_score: AggregatedProductScore,
) -> None:
    existing = session.execute(
        select(ProductScore).where(
            ProductScore.run_id == run_id,
            ProductScore.product_id == aggregated_score.product_id,
        )
    ).scalar_one_or_none()

    if existing is None:
        session.add(
            ProductScore(
                id=str(uuid4()),
                product_id=aggregated_score.product_id,
                run_id=run_id,
                week_start=aggregated_score.week_start,
                trend_score=_quantize(Decimal(aggregated_score.trend_score)),
                viral_potential_score=_quantize(Decimal(aggregated_score.viral_potential_score)),
                creator_accessibility_score=_quantize(
                    Decimal(aggregated_score.creator_accessibility_score)
                ),
                saturation_penalty=aggregated_score.saturation_penalty,
                revenue_estimate=aggregated_score.revenue_estimate,
                final_score=aggregated_score.final_score,
                classification=aggregated_score.classification,
                lifecycle_phase=aggregated_score.lifecycle_phase,
                explainability_payload=aggregated_score.explainability_payload,
                created_at=datetime.now(UTC),
            )
        )
        return

    existing.week_start = aggregated_score.week_start
    existing.trend_score = _quantize(Decimal(aggregated_score.trend_score))
    existing.viral_potential_score = _quantize(Decimal(aggregated_score.viral_potential_score))
    existing.creator_accessibility_score = _quantize(
        Decimal(aggregated_score.creator_accessibility_score)
    )
    existing.saturation_penalty = aggregated_score.saturation_penalty
    existing.revenue_estimate = aggregated_score.revenue_estimate
    existing.final_score = aggregated_score.final_score
    existing.classification = aggregated_score.classification
    existing.lifecycle_phase = aggregated_score.lifecycle_phase
    existing.explainability_payload = aggregated_score.explainability_payload


def persist_aggregated_scores(
    session: Session,
    *,
    run_id: str,
    agent_inputs: list[AgentScoreInput],
    trend_results: list[dict[str, object]],
    viral_results: list[dict[str, object]],
    creator_results: list[dict[str, object]],
    config_version: str,
) -> list[AggregatedProductScore]:
    trend_by_product = _result_index(trend_results)
    viral_by_product = _result_index(viral_results)
    creator_by_product = _result_index(creator_results)

    aggregated_scores: list[AggregatedProductScore] = []
    for agent_input in agent_inputs:
        try:
            trend_result = trend_by_product[agent_input.product_id]
            viral_result = viral_by_product[agent_input.product_id]
            creator_result = creator_by_product[agent_input.product_id]
        except KeyError as exc:
            raise RuntimeError(
                f"Missing agent score payload for product `{agent_input.product_id}` during "
                "final aggregation."
            ) from exc

        aggregated_score = aggregate_score_input(
            agent_input=agent_input,
            trend_result=trend_result,
            viral_result=viral_result,
            creator_result=creator_result,
            config_version=config_version,
        )
        _upsert_product_score(
            session,
            run_id=run_id,
            aggregated_score=aggregated_score,
        )
        aggregated_scores.append(aggregated_score)

    return aggregated_scores
