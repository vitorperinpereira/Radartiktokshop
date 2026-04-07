"""Ranking API service â€” reads latest Report from the database."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.shared.db.models import Report


@dataclass
class _Entry:
    """Flat view of a ranking item, compatible with the router's attribute access."""

    rank: int
    product_id: str
    name: str
    title: str  # alias for frontend compat
    category: str
    final_score: float
    label: str
    trend_score: float
    revenue_score: float
    competition_score: float
    viral_score: float
    decay_factor: float = 1.0
    acceleration_bonus: float = 1.0
    estimated_weekly_commission: float = 0.0
    commission_per_sale: float = 0.0
    days_since_detected: int = 0
    scored_at: str = ""
    region: str = "BR"
    # Extended fields used by product detail / radar card
    image_url: str | None = None
    summary: str | None = None
    summary_text: str | None = None
    lifecycle_phase: str | None = None
    opportunity_window_days: int | None = None
    google_trends_score: float | None = None
    saturation_risk: str | None = None
    revenue_estimate: float | None = None
    risk_flags: list[str] = field(default_factory=list)
    score_breakdown: dict[str, Any] = field(default_factory=dict)
    top_positive_signals: list[str] = field(default_factory=list)
    top_negative_signals: list[str] = field(default_factory=list)
    evidence_highlights: list[str] = field(default_factory=list)
    content_angle: dict[str, Any] = field(default_factory=dict)
    content_angles: list[dict[str, Any]] = field(default_factory=list)
    latest_snapshot: dict[str, Any] | None = None


@dataclass
class _Report:
    week_label: str
    generated_at: str
    entries: list[_Entry]


_LABEL_PT: dict[str, str] = {
    "strong_weekly_bet": "Aposta da Semana",
    "test_selectively": "Testar com Cautela",
    "watchlist_only": "Monitorar",
    "low_priority": "Baixa Prioridade",
    "explosive": "Explosivo",
    "high": "Alta Demanda",
    "medium": "Demanda MÃ©dia",
    "low": "Baixa Demanda",
}

_FLAG_PT: dict[str, str] = {
    "high_saturation": "Alta SaturaÃ§Ã£o",
    "category_noise": "Categoria sem Dados",
    "low_margin_proxy": "Margem Baixa",
    "weak_evidence": "EvidÃªncia Fraca",
    "low_orders": "Poucas Vendas",
    "no_rating": "Sem AvaliaÃ§Ã£o",
}

_RISK_PT: dict[str, str] = {
    "High": "Alto",
    "Medium": "MÃ©dio",
    "Low": "Baixo",
}


def _translate_label(raw: str) -> str:
    return _LABEL_PT.get(raw, raw)


def _translate_flags(flags: list[str]) -> list[str]:
    return [_FLAG_PT.get(f, f) for f in flags]


def _translate_risk(raw: str) -> str:
    return _RISK_PT.get(raw, raw)


def _iso_week_label(week_start: Any) -> str:
    """Convert a date or ISO string to 'YYYY-Www' week label."""
    try:
        if isinstance(week_start, str):
            from datetime import date as _date

            d = _date.fromisoformat(week_start)
        else:
            d = week_start
        return f"{d.isocalendar().year}-W{d.isocalendar().week:02d}"
    except Exception:
        return str(week_start)


def _item_to_entry(item: dict[str, Any]) -> _Entry:
    CATEGORIES_PT = {
        "Beauty": "Beleza e SaÃºde",
        "Home": "Casa e DecoraÃ§Ã£o",
        "Electronics": "EletrÃ´nicos",
        "Kitchen": "Cozinha e Lar",
        "Fitness": "SaÃºde",
        "Fashion": "Moda",
        "Toys": "Brinquedos e Hobbies",
        "Automotive": "Automotivo",
    }

    breakdown = item.get("score_breakdown") or {}
    cat_en = str(item.get("category", "Geral"))
    cat_pt = CATEGORIES_PT.get(cat_en, cat_en)

    latest_snap = item.get("latest_snapshot") or {}
    price = float(latest_snap.get("price") or 0)
    commission_rate = float(
        item.get("commission_amount")
        or item.get("commission")
        or latest_snap.get("commission_rate")
        or 0
    )
    # Only compute real commission â€” never fabricate from price
    comissao_em_reais = (
        round(price * commission_rate, 2) if price > 0 and commission_rate > 0 else 0.0
    )

    product_name = str(item.get("name") or item.get("title") or "Produto Desconhecido")

    return _Entry(
        rank=item.get("rank", 0),
        product_id=item.get("product_id", ""),
        name=product_name,
        title=product_name,
        category=cat_pt,
        final_score=float(item.get("final_score") or 0),
        label=_translate_label(item.get("classification") or item.get("label", "")),
        trend_score=float(breakdown.get("trend") or item.get("trend_score") or 0),
        revenue_score=float(breakdown.get("revenue") or item.get("revenue_score") or 0),
        competition_score=float(
            breakdown.get("creator_accessibility") or item.get("competition_score") or 0
        ),
        viral_score=float(breakdown.get("viral_potential") or item.get("viral_score") or 0),
        decay_factor=float(item.get("decay_factor") or 1.0),
        acceleration_bonus=float(item.get("acceleration_bonus") or 1.0),
        estimated_weekly_commission=float(item.get("revenue_estimate") or 0),
        commission_per_sale=comissao_em_reais,
        days_since_detected=int(item.get("days_since_detected") or 0),
        scored_at=str(item.get("scored_at") or ""),
        region=str(item.get("region") or item.get("country") or "BR"),
        image_url=(
            item.get("image_url")
            or item.get("main_image")
            or item.get("cover")
            or item.get("image")
        ),
        summary=item.get("summary"),
        summary_text=item.get("summary_text"),
        lifecycle_phase=item.get("lifecycle_phase"),
        opportunity_window_days=item.get("opportunity_window_days"),
        google_trends_score=item.get("google_trends_score"),
        saturation_risk=_translate_risk(item.get("saturation_risk") or ""),
        revenue_estimate=item.get("revenue_estimate"),
        risk_flags=_translate_flags(item.get("risk_flags") or []),
        score_breakdown=breakdown,
        top_positive_signals=item.get("top_positive_signals") or [],
        top_negative_signals=item.get("top_negative_signals") or [],
        evidence_highlights=item.get("evidence_highlights") or [],
        content_angle=item.get("content_angle") or {},
        content_angles=item.get("content_angles") or [],
        latest_snapshot=item.get("latest_snapshot"),
    )


class RankingApiService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_latest_report(self) -> _Report | None:
        row = self.session.execute(
            select(Report).order_by(Report.created_at.desc()).limit(1)
        ).scalar_one_or_none()

        if row is None:
            return None

        payload = row.report_payload or {}
        items = payload.get("items") or payload.get("entries") or []
        entries = [_item_to_entry(item) for item in items]
        week_label = payload.get("week_label") or _iso_week_label(
            payload.get("week_start") or row.week_start
        )
        generated_at = payload.get("generated_at") or str(row.created_at)

        return _Report(week_label=week_label, generated_at=generated_at, entries=entries)

    def get_product_entry(self, product_id: str) -> _Entry | None:
        report = self.get_latest_report()
        if report is None:
            return None
        for entry in report.entries:
            if entry.product_id == product_id:
                return entry
        return None
