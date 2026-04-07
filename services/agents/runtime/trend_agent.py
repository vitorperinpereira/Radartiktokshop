"""Deterministic Trend Agent runtime built on persisted signals."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from services.agents.contracts import AgentReasoning, AgentScoreInput, AgentScoreResult
from services.shared.db.models import Product, ProductSignal, ProductSnapshot
from services.workers.feature_extraction import FEATURE_SOURCE_KIND

TREND_AGENT_NAME = "trend"


def _latest_signal_values(session: Session) -> dict[str, dict[str, tuple[Decimal, datetime]]]:
    signals = session.execute(
        select(ProductSignal)
        .where(ProductSignal.source_kind == FEATURE_SOURCE_KIND)
        .order_by(
            ProductSignal.product_id,
            ProductSignal.signal_name,
            ProductSignal.observed_at.desc(),
            ProductSignal.created_at.desc(),
        )
    ).scalars()

    signal_map: dict[str, dict[str, tuple[Decimal, datetime]]] = defaultdict(dict)
    for signal in signals:
        if signal.signal_value is None:
            continue
        by_product = signal_map[signal.product_id]
        by_product.setdefault(signal.signal_name, (signal.signal_value, signal.observed_at))

    return signal_map


def _snapshot_counts(session: Session) -> dict[str, int]:
    rows = session.execute(
        select(ProductSnapshot.product_id, func.count(ProductSnapshot.id)).group_by(
            ProductSnapshot.product_id
        )
    ).all()
    return {product_id: snapshot_count for product_id, snapshot_count in rows}


def load_trend_inputs(session: Session, *, week_start: date) -> list[AgentScoreInput]:
    products = {
        product.id: product
        for product in session.execute(
            select(Product).order_by(Product.title, Product.id)
        ).scalars()
    }
    latest_signals = _latest_signal_values(session)
    snapshot_counts = _snapshot_counts(session)

    inputs: list[AgentScoreInput] = []
    for product_id, signal_values in latest_signals.items():
        product = products.get(product_id)
        if product is None:
            continue

        values_only = {name: value for name, (value, _) in signal_values.items()}
        latest_observed_at = max(observed_at for _, observed_at in signal_values.values())
        inputs.append(
            AgentScoreInput(
                product_id=product.id,
                product_title=product.title,
                brand=product.brand,
                category=product.category,
                subcategory=product.subcategory,
                image_url=product.image_url,
                week_start=week_start,
                snapshot_count=snapshot_counts.get(product.id, 0),
                latest_observed_at=latest_observed_at,
                signal_values=values_only,
            )
        )

    return inputs


def evaluate_trend_input(agent_input: AgentScoreInput) -> AgentScoreResult:
    signal_values = agent_input.signal_values
    orders = signal_values.get("orders_estimate_current", Decimal("0"))
    revenue = signal_values.get("revenue_proxy_current", Decimal("0"))
    rating = signal_values.get("rating_current")

    orders_component = min(45, int(orders / Decimal("5")))
    revenue_component = min(20, int(revenue / Decimal("400")))
    persistence_component = min(20, agent_input.snapshot_count * 10)
    rating_component = 0
    if rating is not None:
        rating_component = min(15, max(0, int((rating - Decimal("4.0")) * Decimal("20"))))

    signal_breakdown = {
        "orders_velocity": orders_component,
        "revenue_proxy": revenue_component,
        "signal_persistence": persistence_component,
        "rating_support": rating_component,
    }
    normalized_score = min(100, sum(signal_breakdown.values()))

    strengths: list[str] = []
    weaknesses: list[str] = []
    evidence = [
        f"orders_estimate_current={int(orders)}",
        f"revenue_proxy_current={revenue.quantize(Decimal('0.01'))}",
        f"snapshot_count={agent_input.snapshot_count}",
    ]
    if rating is not None:
        evidence.append(f"rating_current={rating.quantize(Decimal('0.01'))}")

    if orders_component >= 30:
        strengths.append("Strong demand proxy from recent order volume.")
    if revenue_component >= 12:
        strengths.append("Revenue proxy suggests momentum with monetization support.")
    if rating_component >= 10:
        strengths.append("Rating signal supports sustained buyer interest.")
    if persistence_component >= 20:
        strengths.append("Signal persistence is reinforced across multiple snapshots.")

    risk_flags: list[str] = []
    if agent_input.snapshot_count < 2:
        weaknesses.append("Only one recent snapshot is available, limiting persistence confidence.")
        risk_flags.append("weak_evidence")
    if agent_input.category is None:
        weaknesses.append("Missing category metadata reduces trend contextualization.")
        risk_flags.append("category_noise")
    if rating is None:
        weaknesses.append("No rating signal is available to confirm buyer quality.")
    elif rating < Decimal("4.2"):
        weaknesses.append("Rating support is weaker than stronger trend candidates.")

    if not strengths:
        strengths.append("Signal mix is stable enough to support a baseline trend read.")

    summary = (
        f"Trend score {normalized_score} for {agent_input.product_title} is driven by order and "
        f"revenue proxies, with persistence confidence shaped by {agent_input.snapshot_count} "
        "available snapshot(s)."
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
        agent_name=TREND_AGENT_NAME,
        product_id=agent_input.product_id,
        week_start=agent_input.week_start,
        normalized_score=normalized_score,
        reasoning=reasoning,
    )


def evaluate_trend_candidates(session: Session, week_start: date) -> list[AgentScoreResult]:
    return [
        evaluate_trend_input(agent_input)
        for agent_input in load_trend_inputs(session, week_start=week_start)
    ]
