"""Pipeline run orchestration with frequency-aware window resolution."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from services.orchestration.pipeline import execute_pipeline
from services.shared.db.models import IngestionJob, PipelineRun


@dataclass(frozen=True)
class WeeklyRunSummary:
    run_id: str
    week_start: str
    status: str
    config_version: str
    input_job_count: int
    input_job_ids: list[str]
    products_considered: int
    latest_snapshots: int
    signals_created: int
    trend_products_scored: int
    trend_top_score: int | None
    viral_products_scored: int
    viral_top_score: int | None
    creator_products_scored: int
    creator_top_score: int | None
    final_scores_persisted: int
    saturation_estimates: int
    top_final_score: float | None
    top_classification: str | None
    error_summary: str | None


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _resolve_window_start(
    window_start: date | None,
    *,
    frequency: str,
) -> date:
    if window_start is not None:
        return window_start
    today = datetime.now(UTC).date()
    if frequency == "daily":
        return today
    if frequency == "weekly":
        return today - timedelta(days=today.weekday())
    raise ValueError("`frequency` must be either 'daily' or 'weekly'.")


def _build_config_version(profile: str | None, *, frequency: str) -> str:
    base = f"{frequency}-bootstrap-v1"
    return base if not profile else f"{base}:{profile}"


def _completed_job_ids(session: Session) -> list[str]:
    return list(
        session.scalars(
            select(IngestionJob.id)
            .where(IngestionJob.status == "completed")
            .order_by(IngestionJob.started_at, IngestionJob.id)
        )
    )


def execute_pipeline_run(
    *,
    session_factory: sessionmaker[Session],
    week_start: date | None = None,
    profile: str | None = None,
    frequency: str = "weekly",
) -> WeeklyRunSummary:
    resolved_week_start = _resolve_window_start(week_start, frequency=frequency)
    config_version = _build_config_version(profile, frequency=frequency)
    run_id = str(uuid4())
    with session_factory() as session:
        input_job_ids = _completed_job_ids(session)
        session.add(
            PipelineRun(
                id=run_id,
                week_start=resolved_week_start,
                status="running",
                started_at=_utcnow(),
                finished_at=None,
                input_job_ids=input_job_ids,
                config_version=config_version,
                error_summary=None,
            )
        )
        session.commit()

    try:
        with session_factory() as session:
            final_state = execute_pipeline(
                session,
                resolved_week_start,
                profile,
                run_id=run_id,
                config_version=config_version,
                input_job_ids=input_job_ids,
            )
            pipeline_run = session.get(PipelineRun, run_id)
            if pipeline_run is None:
                raise RuntimeError(f"Pipeline run `{run_id}` was not persisted.")

            pipeline_run.status = final_state["status"]
            pipeline_run.finished_at = _utcnow()
            pipeline_run.error_summary = final_state["error_summary"]
            session.commit()

        return WeeklyRunSummary(
            run_id=final_state["run_id"],
            week_start=final_state["week_start"],
            status=final_state["status"],
            config_version=final_state["config_version"],
            input_job_count=final_state["input_job_count"],
            input_job_ids=final_state["input_job_ids"],
            products_considered=final_state["products_considered"],
            latest_snapshots=final_state["latest_snapshots"],
            signals_created=final_state["signals_created"],
            trend_products_scored=final_state["trend_products_scored"],
            trend_top_score=final_state["trend_top_score"],
            viral_products_scored=final_state["viral_products_scored"],
            viral_top_score=final_state["viral_top_score"],
            creator_products_scored=final_state["creator_products_scored"],
            creator_top_score=final_state["creator_top_score"],
            final_scores_persisted=final_state["final_scores_persisted"],
            saturation_estimates=final_state["saturation_estimates"],
            top_final_score=final_state["top_final_score"],
            top_classification=final_state["top_classification"],
            error_summary=final_state["error_summary"],
        )
    except Exception as exc:
        with session_factory() as session:
            failed_run = session.get(PipelineRun, run_id)
            if failed_run is not None:
                failed_run.status = "failed"
                failed_run.finished_at = _utcnow()
                failed_run.error_summary = str(exc)
                session.commit()

        return WeeklyRunSummary(
            run_id=run_id,
            week_start=resolved_week_start.isoformat(),
            status="failed",
            config_version=config_version,
            input_job_count=len(input_job_ids),
            input_job_ids=input_job_ids,
            products_considered=0,
            latest_snapshots=0,
            signals_created=0,
            trend_products_scored=0,
            trend_top_score=None,
            viral_products_scored=0,
            viral_top_score=None,
            creator_products_scored=0,
            creator_top_score=None,
            final_scores_persisted=0,
            saturation_estimates=0,
            top_final_score=None,
            top_classification=None,
            error_summary=str(exc),
        )


execute_weekly_run = execute_pipeline_run
