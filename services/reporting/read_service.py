"""Read-side services for ranking, product detail, and history APIs."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from scoring.gmv_estimator import estimate_gmv_from_snapshots
from services.shared.db.models import (
    ContentAngle,
    PipelineRun,
    Product,
    ProductScore,
    ProductSignal,
    ProductSnapshot,
    Report,
)


def _decimal_to_float(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _datetime_to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def _risk_flags(score: ProductScore) -> list[str]:
    risk_flags = score.explainability_payload.get("risk_flags")
    if not isinstance(risk_flags, list):
        return []
    return [str(flag) for flag in risk_flags]


def _summary(score: ProductScore) -> str | None:
    summary = score.explainability_payload.get("summary")
    if isinstance(summary, str):
        return summary

    explanation = score.explainability_payload.get("explanation")
    if isinstance(explanation, dict):
        explanation_summary = explanation.get("summary")
        if isinstance(explanation_summary, str):
            return explanation_summary

    return None


def _opportunity_window_days(score: ProductScore) -> int | None:
    payload = score.explainability_payload
    raw_value = payload.get("opportunity_window_days")
    if isinstance(raw_value, int):
        return raw_value
    if isinstance(raw_value, float):
        return int(raw_value)

    saturation_model = payload.get("saturation_model")
    if isinstance(saturation_model, dict):
        nested_value = saturation_model.get("opportunity_window_days")
        if isinstance(nested_value, int):
            return nested_value
        if isinstance(nested_value, float):
            return int(nested_value)
    return None


def _google_trends_score(session: Session, *, product_id: str, score: ProductScore) -> float | None:
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


def _content_angles(
    session: Session,
    *,
    product_id: str,
    week_start: date | None,
    limit: int = 3,
) -> list[dict[str, object]]:
    stmt = (
        select(ContentAngle)
        .where(ContentAngle.product_id == product_id)
        .order_by(ContentAngle.created_at.desc(), ContentAngle.id.desc())
        .limit(limit)
    )
    if week_start is not None:
        stmt = stmt.where(ContentAngle.week_start == week_start)

    rows = session.execute(stmt).scalars().all()
    return [
        {
            "angle_type": row.angle_type,
            "hook_text": row.hook_text,
            "supporting_rationale": row.supporting_rationale,
            "week_start": row.week_start.isoformat(),
        }
        for row in rows
    ]


def _report_summary_text_map(
    session: Session,
    *,
    week_start: date | None,
) -> dict[str, str]:
    stmt = select(Report)
    if week_start is not None:
        stmt = stmt.where(Report.week_start == week_start)

    report = session.execute(
        stmt.order_by(Report.created_at.desc(), Report.id.desc()).limit(1)
    ).scalar_one_or_none()
    if report is None:
        return {}

    payload = report.report_payload or {}
    items = payload.get("items")
    if not isinstance(items, list):
        return {}

    summary_map: dict[str, str] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        product_id = item.get("product_id")
        summary_text = item.get("summary_text")
        if isinstance(product_id, str) and isinstance(summary_text, str) and summary_text.strip():
            summary_map[product_id] = summary_text.strip()
    return summary_map


def _saturation_risk(score: ProductScore) -> str:
    penalty = score.saturation_penalty or Decimal("0")
    if penalty >= Decimal("7"):
        return "High"
    if penalty >= Decimal("4"):
        return "Medium"
    return "Low"


def _resolve_latest_scored_week(session: Session) -> date | None:
    return session.scalar(select(func.max(ProductScore.week_start)))


def _resolve_latest_run_id_for_week(session: Session, *, week_start: date) -> str | None:
    """Return the most recent completed pipeline run_id for a given week."""
    return session.scalar(
        select(PipelineRun.id)
        .where(PipelineRun.week_start == week_start, PipelineRun.status == "completed")
        .order_by(PipelineRun.started_at.desc(), PipelineRun.id.desc())
        .limit(1)
    )


def list_weekly_ranking(
    session: Session,
    *,
    week_start: date | None,
    limit: int,
    category: str | None,
    classification: str | None,
    hide_high_saturation: bool,
) -> dict[str, object]:
    resolved_week = week_start or _resolve_latest_scored_week(session)
    if resolved_week is None:
        return {
            "week_start": None,
            "count": 0,
            "items": [],
        }

    latest_run_id = _resolve_latest_run_id_for_week(session, week_start=resolved_week)
    stmt = (
        select(ProductScore, Product)
        .join(Product, Product.id == ProductScore.product_id)
        .where(ProductScore.week_start == resolved_week)
        .order_by(ProductScore.final_score.desc(), Product.title, Product.id)
    )
    if latest_run_id is not None:
        stmt = stmt.where(ProductScore.run_id == latest_run_id)

    if category is not None:
        stmt = stmt.where(Product.category == category)
    if classification is not None:
        stmt = stmt.where(ProductScore.classification == classification)

    rows = session.execute(stmt).all()
    summary_text_map = _report_summary_text_map(session, week_start=resolved_week)
    items: list[dict[str, object]] = []
    for score, product in rows:
        saturation_risk = _saturation_risk(score)
        if hide_high_saturation and saturation_risk == "High":
            continue

        items.append(
            {
                "product_id": product.id,
                "run_id": score.run_id,
                "week_start": score.week_start.isoformat(),
                "title": product.title,
                "brand": product.brand,
                "category": product.category,
                "subcategory": product.subcategory,
                "image_url": product.image_url,
                "final_score": _decimal_to_float(score.final_score),
                "classification": score.classification,
                "trend_score": _decimal_to_float(score.trend_score),
                "viral_potential_score": _decimal_to_float(score.viral_potential_score),
                "creator_accessibility_score": _decimal_to_float(score.creator_accessibility_score),
                "saturation_penalty": _decimal_to_float(score.saturation_penalty),
                "revenue_estimate": _decimal_to_float(score.revenue_estimate),
                "saturation_risk": saturation_risk,
                "lifecycle_phase": score.lifecycle_phase,
                "opportunity_window_days": _opportunity_window_days(score),
                "risk_flags": _risk_flags(score),
                "summary": _summary(score),
                "summary_text": summary_text_map.get(product.id) or _summary(score),
            }
        )
        if len(items) >= limit:
            break

    return {
        "week_start": resolved_week.isoformat(),
        "count": len(items),
        "items": items,
    }


def get_product_detail(
    session: Session,
    *,
    product_id: str,
    week_start: date | None,
) -> dict[str, object] | None:
    product = session.get(Product, product_id)
    if product is None:
        return None

    stmt = (
        select(ProductScore)
        .where(ProductScore.product_id == product_id)
        .order_by(ProductScore.week_start.desc(), ProductScore.created_at.desc())
    )
    if week_start is not None:
        stmt = stmt.where(ProductScore.week_start == week_start)

    score = session.execute(stmt.limit(1)).scalar_one_or_none()
    if score is None:
        return None

    snapshot = session.execute(
        select(ProductSnapshot)
        .where(ProductSnapshot.product_id == product_id)
        .order_by(ProductSnapshot.captured_at.desc(), ProductSnapshot.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    latest_snapshot = None
    if snapshot is not None:
        latest_snapshot = {
            "captured_at": snapshot.captured_at.isoformat(),
            "price": _decimal_to_float(snapshot.price),
            "orders_estimate": snapshot.orders_estimate,
            "rating": _decimal_to_float(snapshot.rating),
            "commission_rate": _decimal_to_float(snapshot.commission_rate),
            "source_name": snapshot.source_name,
            "source_record_id": snapshot.source_record_id,
        }

    summary_text = _summary(score)
    if week_start is None:
        summary_text_map = _report_summary_text_map(session, week_start=score.week_start)
    else:
        summary_text_map = _report_summary_text_map(session, week_start=week_start)
    summary_text = summary_text_map.get(product_id) or summary_text
    google_trends_score = _google_trends_score(session, product_id=product_id, score=score)
    content_angles = _content_angles(session, product_id=product_id, week_start=score.week_start)

    return {
        "product": {
            "id": product.id,
            "canonical_key": product.canonical_key,
            "title": product.title,
            "brand": product.brand,
            "category": product.category,
            "subcategory": product.subcategory,
            "image_url": product.image_url,
            "status": product.status,
        },
        "score": {
            "run_id": score.run_id,
            "week_start": score.week_start.isoformat(),
            "trend_score": _decimal_to_float(score.trend_score),
            "viral_potential_score": _decimal_to_float(score.viral_potential_score),
            "creator_accessibility_score": _decimal_to_float(score.creator_accessibility_score),
            "saturation_penalty": _decimal_to_float(score.saturation_penalty),
            "revenue_estimate": _decimal_to_float(score.revenue_estimate),
            "final_score": _decimal_to_float(score.final_score),
            "classification": score.classification,
            "lifecycle_phase": score.lifecycle_phase,
            "opportunity_window_days": _opportunity_window_days(score),
            "google_trends_score": google_trends_score,
            "summary_text": summary_text,
            "saturation_risk": _saturation_risk(score),
            "risk_flags": _risk_flags(score),
            "explainability_payload": score.explainability_payload,
        },
        "latest_snapshot": latest_snapshot,
        "summary_text": summary_text,
        "lifecycle_phase": score.lifecycle_phase,
        "opportunity_window_days": _opportunity_window_days(score),
        "google_trends_score": google_trends_score,
        "gmv_estimate": _gmv_estimate(session, product_id=product_id),
        "content_angles": content_angles,
    }


def list_pipeline_run_history(session: Session, *, limit: int) -> dict[str, object]:
    runs = (
        session.execute(
            select(PipelineRun)
            .order_by(PipelineRun.started_at.desc(), PipelineRun.id.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )

    score_rows = (
        session.execute(
            select(ProductScore).order_by(
                ProductScore.run_id,
                ProductScore.final_score.desc(),
                ProductScore.created_at.desc(),
            )
        )
        .scalars()
        .all()
    )
    report_count_rows = session.execute(
        select(Report.run_id, func.count(Report.id)).group_by(Report.run_id)
    ).all()
    report_counts: dict[str, int] = {
        run_id: report_count for run_id, report_count in report_count_rows
    }

    scored_products: dict[str, int] = {}
    top_scores: dict[str, ProductScore] = {}
    for score in score_rows:
        scored_products[score.run_id] = scored_products.get(score.run_id, 0) + 1
        top_scores.setdefault(score.run_id, score)

    items: list[dict[str, object]] = []
    for run in runs:
        duration_seconds = None
        if run.finished_at is not None:
            duration_seconds = int((run.finished_at - run.started_at).total_seconds())

        top_score = top_scores.get(run.id)
        items.append(
            {
                "run_id": run.id,
                "week_start": run.week_start.isoformat(),
                "status": run.status,
                "started_at": run.started_at.isoformat(),
                "finished_at": _datetime_to_iso(run.finished_at),
                "duration_seconds": duration_seconds,
                "input_job_ids": list(run.input_job_ids),
                "config_version": run.config_version,
                "error_summary": run.error_summary,
                "scored_products": scored_products.get(run.id, 0),
                "top_final_score": (
                    None if top_score is None else _decimal_to_float(top_score.final_score)
                ),
                "top_classification": None if top_score is None else top_score.classification,
                "report_count": report_counts.get(run.id, 0),
            }
        )

    return {
        "count": len(items),
        "items": items,
    }


def list_report_history(session: Session, *, limit: int) -> dict[str, object]:
    rows = session.execute(
        select(Report, PipelineRun)
        .join(PipelineRun, PipelineRun.id == Report.run_id)
        .order_by(Report.created_at.desc(), Report.id.desc())
        .limit(limit)
    ).all()

    items = [
        {
            "report_id": report.id,
            "run_id": report.run_id,
            "week_start": report.week_start.isoformat(),
            "status": report.status,
            "created_at": report.created_at.isoformat(),
            "published_at": _datetime_to_iso(report.published_at),
            "pipeline_status": run.status,
            "report_payload": report.report_payload,
            "payload_keys": sorted(report.report_payload.keys()),
        }
        for report, run in rows
    ]
    return {
        "count": len(items),
        "items": items,
    }
