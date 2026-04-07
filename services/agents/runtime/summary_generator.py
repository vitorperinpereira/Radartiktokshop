"""LLM-backed human-readable summary generator."""

from __future__ import annotations

import asyncio
import logging
from decimal import Decimal

from services.agents.prompts.product_summary import PRODUCT_SUMMARY_PROMPT
from services.shared.llm_client import LLM_AVAILABLE, llm_json_call

logger = logging.getLogger(__name__)


def _clip_text(value: str, *, max_length: int) -> str:
    trimmed = value.strip()
    if len(trimmed) <= max_length:
        return trimmed
    return f"{trimmed[: max_length - 3].rstrip()}..."


def _format_price(value: object) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, Decimal):
        return f"{value.quantize(Decimal('0.01'))}"
    return str(value)


def _fallback_summary(product_data: dict[str, object]) -> str:
    title = str(product_data.get("title") or "Este produto")
    classification = str(product_data.get("classification") or "sem classificacao")
    lifecycle_phase = str(product_data.get("lifecycle_phase") or "fase nao informada")
    strengths = product_data.get("strengths")
    weaknesses = product_data.get("weaknesses")

    strength_text = ""
    if isinstance(strengths, list):
        strength_text = " ".join(
            str(strength).strip() for strength in strengths if str(strength).strip()
        )
    weakness_text = ""
    if isinstance(weaknesses, list):
        weakness_text = " ".join(
            str(weakness).strip() for weakness in weaknesses if str(weakness).strip()
        )

    summary = (
        f"{title} hoje esta em {classification} e aparece em {lifecycle_phase}. "
        "O sinal mais importante e que ainda existe janela para testar o produto "
        "enquanto o interesse segue visivel."
    )
    if strength_text:
        summary += f" Destaques: {strength_text}."
    if weakness_text:
        summary += f" Ponto de atencao: {weakness_text}."
    return _clip_text(summary, max_length=320)


def _build_prompt(product_data: dict[str, object]) -> str:
    return PRODUCT_SUMMARY_PROMPT.format(
        title=product_data.get("title") or "Desconhecido",
        category=product_data.get("category") or "geral",
        subcategory=product_data.get("subcategory") or "geral",
        price=_format_price(product_data.get("price")),
        classification=product_data.get("classification") or "unclassified",
        lifecycle_phase=product_data.get("lifecycle_phase") or "UNKNOWN",
        trend_score=int(round(float(product_data.get("trend_score") or 0.0))),
        viral_score=int(round(float(product_data.get("viral_score") or 0.0))),
        accessibility_score=int(round(float(product_data.get("accessibility_score") or 0.0))),
        strengths="; ".join(str(value) for value in product_data.get("strengths", []) or []),
        weaknesses="; ".join(str(value) for value in product_data.get("weaknesses", []) or []),
    )


def _normalize_llm_payload(payload: dict[str, object]) -> str:
    summary_text = payload.get("summary_text")
    if isinstance(summary_text, str) and summary_text.strip():
        return _clip_text(summary_text, max_length=320)
    return ""


async def generate_summary(product_data: dict[str, object]) -> str:
    if not LLM_AVAILABLE:
        return _fallback_summary(product_data)

    prompt = _build_prompt(product_data)
    try:
        llm_result = await asyncio.to_thread(llm_json_call, prompt, 0.4, 400)
        if isinstance(llm_result, dict):
            summary_text = _normalize_llm_payload(llm_result)
            if summary_text:
                return summary_text
    except Exception as exc:
        logger.warning(
            "summary_generator LLM fallback for %s: %s",
            product_data.get("product_id") or product_data.get("title") or "unknown",
            exc,
        )

    return _fallback_summary(product_data)
