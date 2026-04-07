"""Deterministic weekly report builder and export persistence."""

from __future__ import annotations

import asyncio
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from statistics import mean
from uuid import uuid4
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from scoring.gmv_estimator import estimate_gmv_from_snapshots
from services.agents.runtime.summary_generator import generate_summary
from services.shared.db.models import (
    ContentAngle,
    PipelineRun,
    Product,
    ProductScore,
    ProductSignal,
    ProductSnapshot,
    Report,
)

REPORT_VERSION = "report-mvp-v1"
DEFAULT_REPORT_STATUS = "draft"


@dataclass(frozen=True)
class SnapshotContext:
    captured_at: str
    price: float | None
    orders_estimate: int | None
    rating: float | None
    commission_rate: float | None
    source_name: str
    source_record_id: str | None


@dataclass(frozen=True)
class ReportCandidate:
    product_id: str
    title: str
    brand: str | None
    category: str | None
    subcategory: str | None
    image_url: str | None
    final_score: float | None
    classification: str | None
    lifecycle_phase: str | None
    trend_score: float | None
    viral_potential_score: float | None
    creator_accessibility_score: float | None
    saturation_penalty: float | None
    revenue_estimate: float | None
    summary: str | None
    opportunity_window_days: int | None
    google_trends_score: float | None
    risk_flags: list[str]
    top_positive_signals: list[str]
    top_negative_signals: list[str]
    evidence_highlights: list[str]
    latest_snapshot: SnapshotContext | None
    gmv_estimate: float | None
    gmv_caveat: str | None
    summary_text: str | None = None


@dataclass(frozen=True)
class ContentAnglePayload:
    angle_type: str
    hook_text: str
    supporting_rationale: str


@dataclass(frozen=True)
class ReportExportResult:
    report_id: str
    run_id: str
    week_start: str
    status: str
    item_count: int
    report_payload: dict[str, object]


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _decimal_to_float(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _clip_text(value: str, *, max_length: int) -> str:
    trimmed = value.strip()
    if len(trimmed) <= max_length:
        return trimmed
    return f"{trimmed[: max_length - 3].rstrip()}..."


def _summary_from_payload(explainability_payload: dict[str, object]) -> str | None:
    summary = explainability_payload.get("summary")
    if isinstance(summary, str) and summary.strip():
        return summary.strip()

    explanation = explainability_payload.get("explanation")
    if isinstance(explanation, dict):
        nested_summary = explanation.get("summary")
        if isinstance(nested_summary, str) and nested_summary.strip():
            return nested_summary.strip()

    return None


def _int_from_payload(explainability_payload: dict[str, object], key: str) -> int | None:
    raw_value = explainability_payload.get(key)
    if isinstance(raw_value, int):
        return raw_value
    if isinstance(raw_value, float):
        return int(raw_value)
    return None


def _opportunity_window_days(explainability_payload: dict[str, object]) -> int | None:
    window = _int_from_payload(explainability_payload, "opportunity_window_days")
    if window is not None:
        return window

    saturation_model = explainability_payload.get("saturation_model")
    if isinstance(saturation_model, dict):
        return _int_from_payload(saturation_model, "opportunity_window_days")
    return None


def _google_trends_score(session: Session, *, product_id: str) -> float | None:
    signal = session.execute(
        select(ProductSignal)
        .where(
            ProductSignal.product_id == product_id,
            ProductSignal.signal_name == "google_trends_score",
        )
        .order_by(ProductSignal.observed_at.desc(), ProductSignal.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    if signal is None or signal.signal_value is None:
        return None
    return _decimal_to_float(signal.signal_value)


def _google_trends_validation(google_trends_score: float | None, trend_score: float | None) -> bool:
    return bool(
        google_trends_score is not None
        and trend_score is not None
        and google_trends_score > 50
        and trend_score > 70
    )


def _text_list(explainability_payload: dict[str, object], field_name: str) -> list[str]:
    values = explainability_payload.get(field_name)
    if isinstance(values, list):
        return [str(value).strip() for value in values if str(value).strip()]

    explanation = explainability_payload.get("explanation")
    if isinstance(explanation, dict):
        nested_values = explanation.get(field_name)
        if isinstance(nested_values, list):
            return [str(value).strip() for value in nested_values if str(value).strip()]

    return []


def _saturation_risk(saturation_penalty: float | None, risk_flags: list[str]) -> str:
    if "high_saturation" in risk_flags:
        return "High"
    if saturation_penalty is None:
        return "Low"
    if saturation_penalty >= 7:
        return "High"
    if saturation_penalty >= 4:
        return "Medium"
    return "Low"


def _report_timestamp(generated_at: datetime, timezone: str) -> str:
    return generated_at.astimezone(ZoneInfo(timezone)).isoformat()


def _resolve_completed_run(
    session: Session,
    *,
    run_id: str | None,
    week_start: date | None,
) -> PipelineRun:
    if run_id is not None:
        run = session.get(PipelineRun, run_id)
        if run is None:
            raise RuntimeError(f"Pipeline run `{run_id}` was not found.")
        if run.status != "completed":
            raise RuntimeError(f"Pipeline run `{run_id}` is not completed.")
        if week_start is not None and run.week_start != week_start:
            raise RuntimeError(
                f"Pipeline run `{run_id}` does not belong to week `{week_start.isoformat()}`."
            )
        return run

    stmt = select(PipelineRun).where(PipelineRun.status == "completed")
    if week_start is not None:
        stmt = stmt.where(PipelineRun.week_start == week_start)

    run = session.execute(
        stmt.order_by(
            PipelineRun.week_start.desc(),
            PipelineRun.finished_at.desc(),
            PipelineRun.started_at.desc(),
            PipelineRun.id.desc(),
        ).limit(1)
    ).scalar_one_or_none()

    if run is not None:
        return run

    if week_start is not None:
        raise RuntimeError(
            f"No completed pipeline run was found for week `{week_start.isoformat()}`."
        )
    raise RuntimeError("No completed pipeline runs were found for report export.")


def _latest_snapshot(session: Session, *, product_id: str) -> SnapshotContext | None:
    snapshot = session.execute(
        select(ProductSnapshot)
        .where(ProductSnapshot.product_id == product_id)
        .order_by(ProductSnapshot.captured_at.desc(), ProductSnapshot.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    if snapshot is None:
        return None

    return SnapshotContext(
        captured_at=snapshot.captured_at.isoformat(),
        price=_decimal_to_float(snapshot.price),
        orders_estimate=snapshot.orders_estimate,
        rating=_decimal_to_float(snapshot.rating),
        commission_rate=_decimal_to_float(snapshot.commission_rate),
        source_name=snapshot.source_name,
        source_record_id=snapshot.source_record_id,
    )


def _content_angles_for_products(
    session: Session,
    *,
    run_id: str,
    product_ids: list[str],
    limit: int = 3,
) -> dict[str, list[ContentAnglePayload]]:
    if not product_ids:
        return {}

    rows = (
        session.execute(
            select(ContentAngle)
            .where(ContentAngle.run_id == run_id, ContentAngle.product_id.in_(product_ids))
            .order_by(
                ContentAngle.product_id,
                ContentAngle.created_at.desc(),
                ContentAngle.id.desc(),
            )
        )
        .scalars()
        .all()
    )
    grouped: dict[str, list[ContentAnglePayload]] = {}
    for row in rows:
        bucket = grouped.setdefault(row.product_id, [])
        if len(bucket) >= limit:
            continue
        bucket.append(
            ContentAnglePayload(
                angle_type=row.angle_type,
                hook_text=row.hook_text,
                supporting_rationale=row.supporting_rationale or "",
            )
        )
    return grouped


def _gmv_estimate(session: Session, *, product_id: str) -> float | None:
    snapshots = (
        session.execute(
            select(ProductSnapshot)
            .where(ProductSnapshot.product_id == product_id)
            .order_by(ProductSnapshot.captured_at.asc(), ProductSnapshot.created_at.asc())
        )
        .scalars()
        .all()
    )
    if len(snapshots) < 2:
        return None

    snapshot_payloads: list[dict[str, object]] = []
    for snapshot in snapshots:
        snapshot_payloads.append(
            {
                "captured_at": snapshot.captured_at.isoformat(),
                "stock_count": (
                    int(snapshot.raw_payload["stock_count"])
                    if isinstance(snapshot.raw_payload, dict)
                    and "stock_count" in snapshot.raw_payload
                    and snapshot.raw_payload["stock_count"] is not None
                    else None
                ),
                "price": _decimal_to_float(snapshot.price),
            }
        )

    estimate = estimate_gmv_from_snapshots(snapshot_payloads)
    return None if estimate is None else float(estimate)


async def _generate_summary_text(candidate: ReportCandidate) -> str:
    return await generate_summary(
        {
            "product_id": candidate.product_id,
            "title": candidate.title,
            "category": candidate.category,
            "subcategory": candidate.subcategory,
            "price": None if candidate.latest_snapshot is None else candidate.latest_snapshot.price,
            "classification": candidate.classification,
            "lifecycle_phase": candidate.lifecycle_phase,
            "trend_score": candidate.trend_score,
            "viral_score": candidate.viral_potential_score,
            "accessibility_score": candidate.creator_accessibility_score,
            "strengths": candidate.top_positive_signals,
            "weaknesses": candidate.top_negative_signals,
        }
    )


def _load_report_candidates(
    session: Session,
    *,
    run: PipelineRun,
    limit: int,
) -> list[ReportCandidate]:
    rows = session.execute(
        select(ProductScore, Product)
        .join(Product, Product.id == ProductScore.product_id)
        .where(ProductScore.run_id == run.id)
        .order_by(ProductScore.final_score.desc(), Product.title, Product.id)
        .limit(limit)
    ).all()

    if not rows:
        raise RuntimeError(f"No persisted product scores were found for run `{run.id}`.")

    candidates: list[ReportCandidate] = []
    for score, product in rows:
        explainability_payload = score.explainability_payload
        google_trends_score = _google_trends_score(session, product_id=product.id)
        candidates.append(
            ReportCandidate(
                product_id=product.id,
                title=product.title,
                brand=product.brand,
                category=product.category,
                subcategory=product.subcategory,
                image_url=product.image_url,
                final_score=_decimal_to_float(score.final_score),
                classification=score.classification,
                lifecycle_phase=score.lifecycle_phase,
                trend_score=_decimal_to_float(score.trend_score),
                viral_potential_score=_decimal_to_float(score.viral_potential_score),
                creator_accessibility_score=_decimal_to_float(score.creator_accessibility_score),
                saturation_penalty=_decimal_to_float(score.saturation_penalty),
                revenue_estimate=_decimal_to_float(score.revenue_estimate),
                summary=_summary_from_payload(explainability_payload),
                opportunity_window_days=_opportunity_window_days(explainability_payload),
                google_trends_score=google_trends_score,
                risk_flags=_text_list(explainability_payload, "risk_flags"),
                top_positive_signals=_text_list(explainability_payload, "top_positive_signals"),
                top_negative_signals=_text_list(explainability_payload, "top_negative_signals"),
                evidence_highlights=_text_list(explainability_payload, "evidence"),
                latest_snapshot=_latest_snapshot(session, product_id=product.id),
                gmv_estimate=_gmv_estimate(session, product_id=product.id),
                gmv_caveat=(
                    "Estimativa direcional — reposições e carrinhos abandonados podem distorcer."
                ),
            )
        )

    return candidates


def _angle_type(candidate: ReportCandidate) -> str:
    dominant_score = max(
        (
            ("momentum_hook", candidate.trend_score or 0.0),
            ("demo_hook", candidate.viral_potential_score or 0.0),
            ("accessibility_hook", candidate.creator_accessibility_score or 0.0),
        ),
        key=lambda item: (item[1], item[0]),
    )
    if dominant_score[1] <= 0:
        return "balanced_hook"
    return dominant_score[0]


def build_content_angle(candidate: ReportCandidate) -> ContentAnglePayload:
    angle_type = _angle_type(candidate)
    lead_reason = (
        (candidate.top_positive_signals[0] if candidate.top_positive_signals else None)
        or candidate.summary
        or "the current score mix stayed stable across the persisted weekly signals."
    )
    lead_reason = _clip_text(lead_reason, max_length=160)

    if angle_type == "demo_hook":
        hook_text = f"Why {candidate.title} stands out on camera this week: {lead_reason}"
    elif angle_type == "momentum_hook":
        hook_text = f"Why {candidate.title} is gaining attention this week: {lead_reason}"
    elif angle_type == "accessibility_hook":
        hook_text = f"Why {candidate.title} looks approachable for smaller creators: {lead_reason}"
    else:
        hook_text = f"Why {candidate.title} made this week's radar: {lead_reason}"

    supporting_rationale = _clip_text(candidate.summary or lead_reason, max_length=220)
    return ContentAnglePayload(
        angle_type=angle_type,
        hook_text=hook_text,
        supporting_rationale=supporting_rationale,
    )


def build_report_payload(
    *,
    run_id: str,
    week_start: date,
    candidates: list[ReportCandidate],
    timezone: str,
    generated_at: datetime | None = None,
    content_angles_by_product: dict[str, list[ContentAnglePayload]] | None = None,
) -> dict[str, object]:
    if not candidates:
        raise RuntimeError("Cannot build a report payload without ranked candidates.")

    resolved_generated_at = generated_at or _utcnow()
    top_candidate = candidates[0]
    final_scores = [
        candidate.final_score for candidate in candidates if candidate.final_score is not None
    ]
    average_final_score = round(mean(final_scores), 2) if final_scores else None
    category_counts = Counter(
        candidate.category or "unknown" for candidate in candidates if candidate.category
    )
    classification_counts = Counter(
        candidate.classification or "unclassified" for candidate in candidates
    )
    high_saturation_count = sum(
        1
        for candidate in candidates
        if _saturation_risk(candidate.saturation_penalty, candidate.risk_flags) == "High"
    )
    angles_by_product = content_angles_by_product or {}
    methodology_disclaimer = (
        "Scores são estimativas direcionais baseadas em sinais públicos. GMV estimado "
        "NÃO é lucro real - reposições de estoque, devoluções e carrinhos abandonados "
        "podem distorcer os números. Use como bússola, não como GPS."
    )
    data_freshness = (
        "Dados atualizados a cada weekly run. Tendências no TikTok saturam em dias - "
        "aja rápido sobre produtos EMERGENTES."
    )

    payload_items: list[dict[str, object]] = []
    for rank, candidate in enumerate(candidates, start=1):
        content_angle = build_content_angle(candidate)
        product_content_angles = angles_by_product.get(candidate.product_id) or [content_angle]
        summary_text = asyncio.run(_generate_summary_text(candidate))
        google_trends_validation = _google_trends_validation(
            candidate.google_trends_score,
            candidate.trend_score,
        )
        payload_items.append(
            {
                "rank": rank,
                "product_id": candidate.product_id,
                "title": candidate.title,
                "brand": candidate.brand,
                "category": candidate.category,
                "subcategory": candidate.subcategory,
                "image_url": candidate.image_url,
                "final_score": candidate.final_score,
                "classification": candidate.classification,
                "lifecycle_phase": candidate.lifecycle_phase,
                "summary": candidate.summary,
                "saturation_penalty": candidate.saturation_penalty,
                "saturation_risk": _saturation_risk(
                    candidate.saturation_penalty,
                    candidate.risk_flags,
                ),
                "opportunity_window_days": candidate.opportunity_window_days,
                "revenue_estimate": candidate.revenue_estimate,
                "gmv_estimate": candidate.gmv_estimate,
                "gmv_caveat": candidate.gmv_caveat,
                "google_trends_score": candidate.google_trends_score,
                "google_trends_validation": google_trends_validation,
                "summary_text": summary_text,
                "risk_flags": candidate.risk_flags,
                "score_breakdown": {
                    "trend": candidate.trend_score,
                    "viral_potential": candidate.viral_potential_score,
                    "creator_accessibility": candidate.creator_accessibility_score,
                    "final": candidate.final_score,
                },
                "content_angle": {
                    "angle_type": content_angle.angle_type,
                    "hook_text": content_angle.hook_text,
                    "supporting_rationale": content_angle.supporting_rationale,
                },
                "content_angles": [
                    {
                        "angle_type": angle.angle_type,
                        "hook_text": angle.hook_text,
                        "supporting_rationale": angle.supporting_rationale,
                    }
                    for angle in product_content_angles[:3]
                ],
                "top_positive_signals": candidate.top_positive_signals[:3],
                "top_negative_signals": candidate.top_negative_signals[:3],
                "evidence_highlights": candidate.evidence_highlights[:3],
                "latest_snapshot": (
                    None
                    if candidate.latest_snapshot is None
                    else {
                        "captured_at": candidate.latest_snapshot.captured_at,
                        "price": candidate.latest_snapshot.price,
                        "orders_estimate": candidate.latest_snapshot.orders_estimate,
                        "rating": candidate.latest_snapshot.rating,
                        "commission_rate": candidate.latest_snapshot.commission_rate,
                        "source_name": candidate.latest_snapshot.source_name,
                        "source_record_id": candidate.latest_snapshot.source_record_id,
                    }
                ),
            }
        )

    return {
        "report_version": REPORT_VERSION,
        "run_id": run_id,
        "week_start": week_start.isoformat(),
        "generated_at": _report_timestamp(resolved_generated_at, timezone),
        "timezone": timezone,
        "methodology_disclaimer": methodology_disclaimer,
        "data_freshness": data_freshness,
        "summary": {
            "headline": (
                f"{top_candidate.title} leads {len(candidates)} ranked products for "
                f"week {week_start.isoformat()}."
            ),
            "item_count": len(candidates),
            "average_final_score": average_final_score,
            "top_final_score": top_candidate.final_score,
            "high_saturation_count": high_saturation_count,
            "classification_counts": dict(sorted(classification_counts.items())),
            "category_mix": [
                {"category": category, "count": count}
                for category, count in sorted(
                    category_counts.items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ],
        },
        "items": payload_items,
    }


def _upsert_content_angle(
    session: Session,
    *,
    run: PipelineRun,
    candidate: ReportCandidate,
    content_angle: ContentAnglePayload,
    created_at: datetime,
) -> None:
    existing = session.execute(
        select(ContentAngle)
        .where(
            ContentAngle.run_id == run.id,
            ContentAngle.product_id == candidate.product_id,
        )
        .limit(1)
    ).scalar_one_or_none()

    if existing is None:
        session.add(
            ContentAngle(
                id=str(uuid4()),
                product_id=candidate.product_id,
                week_start=run.week_start,
                run_id=run.id,
                angle_type=content_angle.angle_type,
                hook_text=content_angle.hook_text,
                supporting_rationale=content_angle.supporting_rationale,
                created_at=created_at,
            )
        )
        return

    existing.week_start = run.week_start
    existing.angle_type = content_angle.angle_type
    existing.hook_text = content_angle.hook_text
    existing.supporting_rationale = content_angle.supporting_rationale
    existing.created_at = created_at


def _upsert_report(
    session: Session,
    *,
    run: PipelineRun,
    report_payload: dict[str, object],
    created_at: datetime,
) -> Report:
    existing = session.execute(
        select(Report)
        .where(
            Report.run_id == run.id,
            Report.status == DEFAULT_REPORT_STATUS,
        )
        .limit(1)
    ).scalar_one_or_none()

    if existing is None:
        report = Report(
            id=str(uuid4()),
            week_start=run.week_start,
            run_id=run.id,
            status=DEFAULT_REPORT_STATUS,
            report_payload=report_payload,
            published_at=None,
            created_at=created_at,
        )
        session.add(report)
        session.flush()
        return report

    existing.week_start = run.week_start
    existing.report_payload = report_payload
    existing.published_at = None
    existing.created_at = created_at
    session.flush()
    return existing


def export_weekly_report(
    session: Session,
    *,
    run_id: str | None = None,
    week_start: date | None = None,
    limit: int = 10,
    timezone: str,
) -> ReportExportResult:
    if limit < 1:
        raise ValueError("Report export limit must be greater than zero.")

    run = _resolve_completed_run(session, run_id=run_id, week_start=week_start)
    generated_at = _utcnow()
    candidates = _load_report_candidates(session, run=run, limit=limit)

    for candidate in candidates:
        _upsert_content_angle(
            session,
            run=run,
            candidate=candidate,
            content_angle=build_content_angle(candidate),
            created_at=generated_at,
        )

    content_angles_by_product = _content_angles_for_products(
        session,
        run_id=run.id,
        product_ids=[candidate.product_id for candidate in candidates],
    )
    report_payload = build_report_payload(
        run_id=run.id,
        week_start=run.week_start,
        candidates=candidates,
        timezone=timezone,
        generated_at=generated_at,
        content_angles_by_product=content_angles_by_product,
    )

    report = _upsert_report(
        session,
        run=run,
        report_payload=report_payload,
        created_at=generated_at,
    )
    session.commit()

    return ReportExportResult(
        report_id=report.id,
        run_id=run.id,
        week_start=run.week_start.isoformat(),
        status=report.status,
        item_count=len(candidates),
        report_payload=report_payload,
    )
