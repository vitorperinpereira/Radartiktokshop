"""LLM-backed generator for persisted content angles."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from services.agents.prompts.content_angles import CONTENT_ANGLE_PROMPT
from services.shared.db.models import ContentAngle, Product, ProductScore, ProductSnapshot
from services.shared.llm_client import LLM_AVAILABLE, llm_json_call

logger = logging.getLogger(__name__)

CONTENT_ANGLE_TARGET_CLASSIFICATIONS = ("breakout_candidate", "strong_weekly_bet")


def _clip_text(value: str, *, max_length: int) -> str:
    trimmed = value.strip()
    if len(trimmed) <= max_length:
        return trimmed
    return f"{trimmed[: max_length - 3].rstrip()}..."


def _latest_price(session: Session, *, product_id: str) -> Decimal | None:
    snapshot = session.execute(
        select(ProductSnapshot.price)
        .where(ProductSnapshot.product_id == product_id)
        .order_by(ProductSnapshot.captured_at.desc(), ProductSnapshot.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    return snapshot


def _context_strengths(explainability_payload: dict[str, object]) -> list[str]:
    strengths = explainability_payload.get("top_positive_signals")
    if isinstance(strengths, list):
        return [str(strength).strip() for strength in strengths if str(strength).strip()]
    explanation = explainability_payload.get("explanation")
    if isinstance(explanation, dict):
        nested_strengths = explanation.get("strengths")
        if isinstance(nested_strengths, list):
            return [str(strength).strip() for strength in nested_strengths if str(strength).strip()]
    return []


def _context_weaknesses(explainability_payload: dict[str, object]) -> list[str]:
    weaknesses = explainability_payload.get("top_negative_signals")
    if isinstance(weaknesses, list):
        return [str(weakness).strip() for weakness in weaknesses if str(weakness).strip()]
    explanation = explainability_payload.get("explanation")
    if isinstance(explanation, dict):
        nested_weaknesses = explanation.get("weaknesses")
        if isinstance(nested_weaknesses, list):
            return [
                str(weakness).strip() for weakness in nested_weaknesses if str(weakness).strip()
            ]
    return []


def _summary_text(explainability_payload: dict[str, object]) -> str:
    summary = explainability_payload.get("summary")
    if isinstance(summary, str) and summary.strip():
        return summary.strip()
    explanation = explainability_payload.get("explanation")
    if isinstance(explanation, dict):
        nested_summary = explanation.get("summary")
        if isinstance(nested_summary, str) and nested_summary.strip():
            return nested_summary.strip()
    return "No summary available."


def _build_prompt(
    *,
    title: str,
    category: str | None,
    price: Decimal | None,
    viral_score: float,
    accessibility_score: float,
    classification: str,
    strengths: list[str],
) -> str:
    price_value = "N/A" if price is None else f"{price.quantize(Decimal('0.01'))}"
    return CONTENT_ANGLE_PROMPT.format(
        title=title,
        category=category or "geral",
        price=price_value,
        viral_score=int(round(viral_score)),
        accessibility_score=int(round(accessibility_score)),
        classification=classification,
        strengths="; ".join(strengths[:3]) or "sem destaques registrados",
    )


def _normalize_llm_payload(payload: dict[str, object]) -> list[dict[str, str]]:
    angles = payload.get("angles")
    if not isinstance(angles, list):
        return []

    normalized: list[dict[str, str]] = []
    for angle in angles[:3]:
        if not isinstance(angle, dict):
            continue

        script_outline = angle.get("script_outline")
        if isinstance(script_outline, list):
            outline_text = "\n".join(
                f"- {str(line).strip()}" for line in script_outline if str(line).strip()
            )
        else:
            outline_text = str(script_outline or "").strip()

        rationale = str(angle.get("rationale") or "").strip()
        supporting_rationale = rationale
        if outline_text:
            supporting_rationale = f"{rationale}\n{outline_text}" if rationale else outline_text

        normalized.append(
            {
                "angle_type": str(angle.get("type") or "review").strip() or "review",
                "hook_text": str(angle.get("hook_text") or "").strip(),
                "supporting_rationale": _clip_text(
                    supporting_rationale or rationale or "",
                    max_length=500,
                ),
            }
        )
    return normalized


def _fallback_angles(
    *,
    title: str,
    summary: str,
    strengths: list[str],
    weaknesses: list[str],
    classification: str,
    viral_score: float,
    accessibility_score: float,
) -> list[dict[str, str]]:
    lead_strength = strengths[0] if strengths else summary
    lead_weakness = weaknesses[0] if weaknesses else "Ainda vale validar com um teste curto."
    score_blend = int(round((viral_score + accessibility_score) / 2))
    if score_blend >= 80 or classification == "breakout_candidate":
        primary_type = "antes_depois"
        secondary_type = "review"
    elif score_blend >= 65 or classification == "strong_weekly_bet":
        primary_type = "review"
        secondary_type = "tutorial_rapido"
    else:
        primary_type = "pov"
        secondary_type = "unboxing"

    return [
        {
            "angle_type": primary_type,
            "hook_text": f"Testei {title} e o resultado aparece na camera em segundos.",
            "supporting_rationale": _clip_text(
                f"{lead_strength} {summary}",
                max_length=500,
            ),
        },
        {
            "angle_type": secondary_type,
            "hook_text": f"Por que {title} chama atencao de creator pequeno agora.",
            "supporting_rationale": _clip_text(
                f"{lead_strength} {lead_weakness}",
                max_length=500,
            ),
        },
        {
            "angle_type": "comparacao",
            "hook_text": f"Compare {title} com uma alternativa comum e veja a diferenca.",
            "supporting_rationale": _clip_text(
                f"{summary} {lead_strength}",
                max_length=500,
            ),
        },
    ]


async def _generate_with_llm(prompt: str) -> list[dict[str, str]]:
    llm_result = await asyncio.to_thread(llm_json_call, prompt, 0.7, 600)
    if not isinstance(llm_result, dict):
        raise TypeError("llm_json_call returned a non-dict payload")
    return _normalize_llm_payload(llm_result)


def _eligible_scores(
    session: Session,
    *,
    run_id: str,
    limit: int,
) -> list[tuple[ProductScore, Product]]:
    base_stmt = (
        select(ProductScore, Product)
        .join(Product, Product.id == ProductScore.product_id)
        .where(ProductScore.run_id == run_id)
        .order_by(ProductScore.final_score.desc(), Product.title, Product.id)
    )
    preferred_rows = session.execute(
        base_stmt.where(
            ProductScore.classification.in_(CONTENT_ANGLE_TARGET_CLASSIFICATIONS)
        ).limit(limit)
    ).all()
    if preferred_rows:
        return preferred_rows
    return session.execute(base_stmt.limit(limit)).all()


def generate_angles_for_product(
    session: Session,
    *,
    product_id: str,
    title: str,
    category: str | None,
    price: Decimal | None,
    viral_score: int,
    accessibility_score: int,
    classification: str,
    strengths: list[str],
    run_id: str,
    week_start: date,
) -> list[ContentAngle]:
    summary_text = _summary_text({"summary": "; ".join(strengths)})
    fallback_angles = _fallback_angles(
        title=title,
        summary=summary_text,
        strengths=strengths,
        weaknesses=[],
        classification=classification,
        viral_score=viral_score,
        accessibility_score=accessibility_score,
    )

    prompt = _build_prompt(
        title=title,
        category=category,
        price=price,
        viral_score=viral_score,
        accessibility_score=accessibility_score,
        classification=classification,
        strengths=strengths,
    )

    generated_angles: list[dict[str, str]] = []
    if LLM_AVAILABLE:
        try:
            generated_angles = asyncio.run(_generate_with_llm(prompt))
        except Exception as exc:
            logger.warning("content_angle_generator LLM fallback for %s: %s", product_id, exc)

    if not generated_angles:
        generated_angles = fallback_angles
    elif len(generated_angles) < 3:
        generated_angles.extend(fallback_angles[len(generated_angles) : 3])

    session.execute(
        delete(ContentAngle).where(
            ContentAngle.run_id == run_id,
            ContentAngle.product_id == product_id,
        )
    )

    created_at = datetime.now(UTC)
    content_angles: list[ContentAngle] = []
    for angle in generated_angles[:3]:
        content_angle = ContentAngle(
            id=str(uuid4()),
            product_id=product_id,
            week_start=week_start,
            run_id=run_id,
            angle_type=angle["angle_type"],
            hook_text=angle["hook_text"],
            supporting_rationale=angle["supporting_rationale"],
            created_at=created_at,
        )
        session.add(content_angle)
        content_angles.append(content_angle)

    session.flush()
    return content_angles


def generate_angles_for_top_products(
    session: Session,
    *,
    run_id: str,
    week_start: date,
    limit: int = 20,
) -> list[ContentAngle]:
    rows = _eligible_scores(session, run_id=run_id, limit=limit)
    if not rows:
        logger.info("No scored products were available for content angle generation.")
        return []

    generated: list[ContentAngle] = []
    for score, product in rows:
        explainability_payload = score.explainability_payload
        viral_score = float(score.viral_potential_score or 0.0)
        accessibility_score = float(score.creator_accessibility_score or 0.0)
        strengths = _context_strengths(explainability_payload)
        weaknesses = _context_weaknesses(explainability_payload)
        price = _latest_price(session, product_id=product.id)
        generated.extend(
            generate_angles_for_product(
                session,
                product_id=product.id,
                title=product.title,
                category=product.category,
                price=price,
                viral_score=int(round(viral_score)),
                accessibility_score=int(round(accessibility_score)),
                classification=score.classification or "unclassified",
                strengths=strengths or [_summary_text(explainability_payload)],
                run_id=run_id,
                week_start=week_start,
            )
        )
        logger.debug(
            "Generated %d content angles for %s using %d strengths and %d weaknesses.",
            len(generated[-3:]),
            product.id,
            len(strengths),
            len(weaknesses),
        )

    logger.info("Generated %d content angles for run %s.", len(generated), run_id)
    return generated
