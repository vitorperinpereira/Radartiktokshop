"""Read-only dashboard adapter and view helpers for persisted score data."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date

import pandas as pd  # type: ignore[import-untyped]
from sqlalchemy.orm import Session, sessionmaker

from apps.api.schemas import (
    PipelineRunHistoryResponse,
    ProductDetailResponse,
    RankingItem,
    RankingResponse,
)
from services.reporting.read_service import (
    get_product_detail,
    list_pipeline_run_history,
    list_weekly_ranking,
)
from services.shared.config import AppSettings
from services.shared.db import build_session_factory

DEFAULT_RANKING_LIMIT = 100
_UNCATEGORIZED_LABEL = "Sem categoria"
_AGENT_REASONING_KEYS = (
    "trend",
    "viral_potential",
    "creator_accessibility",
)


@dataclass(frozen=True)
class DashboardReadResult[T]:
    """Wrap dashboard reads so pages can handle empty, error, and not-found states."""

    data: T | None = None
    error: str | None = None
    missing: bool = False


@dataclass(frozen=True)
class ExplanationView:
    """Normalized persisted explainability sections for the drilldown page."""

    summary: str | None
    top_positive_signals: list[str] = field(default_factory=list)
    top_negative_signals: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AgentReasoningView:
    """Normalized per-agent reasoning for the drilldown tabs."""

    summary: str | None
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    signal_breakdown: dict[str, int] = field(default_factory=dict)


def _session_factory(
    *,
    settings: AppSettings | None = None,
    session_factory: sessionmaker[Session] | None = None,
) -> sessionmaker[Session]:
    if session_factory is not None:
        return session_factory
    return build_session_factory(settings=settings)


def _parse_week_start(week_start: str | None) -> date | None:
    if week_start is None or week_start == "":
        return None
    return date.fromisoformat(week_start)


def _coerce_text_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _coerce_signal_breakdown(value: object) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}

    signal_breakdown: dict[str, int] = {}
    for key, raw_value in value.items():
        try:
            signal_breakdown[str(key)] = int(raw_value)
        except (TypeError, ValueError):
            continue
    return signal_breakdown


def category_label(category: str | None) -> str:
    return category or _UNCATEGORIZED_LABEL


def load_rankings(
    *,
    settings: AppSettings | None = None,
    session_factory: sessionmaker[Session] | None = None,
    week_start: str | None = None,
    limit: int = DEFAULT_RANKING_LIMIT,
) -> DashboardReadResult[RankingResponse]:
    """Load persisted rankings using the API read contract."""

    try:
        resolved_week = _parse_week_start(week_start)
        with _session_factory(settings=settings, session_factory=session_factory)() as session:
            payload = list_weekly_ranking(
                session,
                week_start=resolved_week,
                limit=limit,
                category=None,
                classification=None,
                hide_high_saturation=False,
            )
    except Exception as exc:  # pragma: no cover - defensive surface for Streamlit
        return DashboardReadResult(
            error=f"Unable to load Weekly Radar data from persisted scores: {exc}"
        )

    return DashboardReadResult(data=RankingResponse.model_validate(payload))


def load_product_detail(
    product_id: str,
    *,
    settings: AppSettings | None = None,
    session_factory: sessionmaker[Session] | None = None,
    week_start: str | None = None,
) -> DashboardReadResult[ProductDetailResponse]:
    """Load one persisted product detail using the API read contract."""

    try:
        resolved_week = _parse_week_start(week_start)
        with _session_factory(settings=settings, session_factory=session_factory)() as session:
            payload = get_product_detail(
                session,
                product_id=product_id,
                week_start=resolved_week,
            )
    except Exception as exc:  # pragma: no cover - defensive surface for Streamlit
        return DashboardReadResult(
            error=f"Unable to load Product Drilldown data from persisted scores: {exc}"
        )

    if payload is None:
        return DashboardReadResult(missing=True)

    return DashboardReadResult(data=ProductDetailResponse.model_validate(payload))


def load_pipeline_history(
    *,
    settings: AppSettings | None = None,
    session_factory: sessionmaker[Session] | None = None,
    limit: int = DEFAULT_RANKING_LIMIT,
) -> DashboardReadResult[PipelineRunHistoryResponse]:
    """Load persisted pipeline history using the API read contract."""

    try:
        with _session_factory(settings=settings, session_factory=session_factory)() as session:
            payload = list_pipeline_run_history(session, limit=limit)
    except Exception as exc:  # pragma: no cover - defensive surface for Streamlit
        return DashboardReadResult(
            error=f"Unable to load pipeline history from persisted scores: {exc}"
        )

    return DashboardReadResult(data=PipelineRunHistoryResponse.model_validate(payload))


def available_categories(items: Sequence[RankingItem]) -> list[str]:
    """Return sorted category labels used by the Weekly Radar filter."""

    return sorted({category_label(item.category) for item in items})


def filter_ranking_items(
    items: Sequence[RankingItem],
    *,
    categories: Sequence[str],
    hide_high_saturation: bool,
) -> list[RankingItem]:
    """Apply dashboard-side filters while preserving persisted score order."""

    selected_categories = set(categories)
    filtered_items: list[RankingItem] = []
    for item in items:
        if selected_categories and category_label(item.category) not in selected_categories:
            continue
        if hide_high_saturation and item.saturation_risk == "High":
            continue
        filtered_items.append(item)
    return filtered_items


def ranking_items_to_dataframe(items: Sequence[RankingItem]) -> pd.DataFrame:
    """Map ranking response items into the Weekly Radar table."""

    return pd.DataFrame(
        [
            {
                "Produto": item.title,
                "ID do Produto": item.product_id,
                "Marca": item.brand or "Desconhecida",
                "Categoria": category_label(item.category),
                "Classificação": item.classification or "sem classificação",
                "Score de Oportunidade": item.final_score,
                "Score de Tendência": item.trend_score,
                "Score Viral": item.viral_potential_score,
                "Score de Acessibilidade": item.creator_accessibility_score,
                "Risco de Saturação": item.saturation_risk,
                "Penalidade de Saturação": item.saturation_penalty,
                "Estimativa de Receita": item.revenue_estimate,
                "Resumo": item.summary or "Sem resumo disponível.",
            }
            for item in items
        ]
    )


def product_option_label(item: RankingItem) -> str:
    score_label = "n/a" if item.final_score is None else f"{item.final_score:.1f}"
    return f"{item.title} [{item.product_id}] | {category_label(item.category)} | {score_label}"


def extract_explanation(detail: ProductDetailResponse) -> ExplanationView:
    """Normalize persisted explainability sections with safe fallbacks."""

    payload = detail.score.explainability_payload
    explanation = payload.get("explanation")
    explanation_dict = explanation if isinstance(explanation, dict) else {}
    summary = payload.get("summary")
    resolved_summary = summary if isinstance(summary, str) else None
    if resolved_summary is None:
        explanation_summary = explanation_dict.get("summary")
        if isinstance(explanation_summary, str):
            resolved_summary = explanation_summary

    return ExplanationView(
        summary=resolved_summary,
        top_positive_signals=_coerce_text_list(payload.get("top_positive_signals")),
        top_negative_signals=_coerce_text_list(payload.get("top_negative_signals")),
        strengths=_coerce_text_list(explanation_dict.get("strengths")),
        weaknesses=_coerce_text_list(explanation_dict.get("weaknesses")),
        evidence=_coerce_text_list(explanation_dict.get("evidence")),
    )


def extract_agent_reasoning(
    detail: ProductDetailResponse,
) -> dict[str, AgentReasoningView]:
    """Normalize per-agent reasoning from the stored explainability payload."""

    payload = detail.score.explainability_payload
    reasoning = payload.get("agent_reasoning")
    reasoning_dict = reasoning if isinstance(reasoning, dict) else {}

    sections: dict[str, AgentReasoningView] = {}
    for key in _AGENT_REASONING_KEYS:
        raw_section = reasoning_dict.get(key)
        section = raw_section if isinstance(raw_section, dict) else {}
        summary = section.get("summary")
        sections[key] = AgentReasoningView(
            summary=summary if isinstance(summary, str) else None,
            strengths=_coerce_text_list(section.get("strengths")),
            weaknesses=_coerce_text_list(section.get("weaknesses")),
            evidence=_coerce_text_list(section.get("evidence")),
            signal_breakdown=_coerce_signal_breakdown(section.get("signal_breakdown")),
        )
    return sections
