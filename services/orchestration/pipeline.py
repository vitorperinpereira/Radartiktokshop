"""Sequential orchestration pipeline for weekly bootstrap runs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import cast
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.agents import (
    evaluate_creator_accessibility_candidates,
    evaluate_trend_candidates,
    evaluate_viral_potential_candidates,
    load_trend_inputs,
)
from services.agents.runtime.content_angle_generator import generate_angles_for_top_products
from services.agents.runtime.saturation_agent import estimate_saturation_for_top_products
from services.orchestration.state import WeeklyRunState, build_initial_weekly_run_state
from services.scoring import persist_aggregated_scores
from services.shared.llm_client import LLM_AVAILABLE
from services.workers.feature_extraction import (
    FeatureExtractionSummary,
    extract_latest_snapshot_signals,
)


@dataclass(frozen=True)
class PipelineConfig:
    run_id: str
    week_start: date
    profile: str | None
    config_version: str
    input_job_ids: list[str]


def _completed_job_ids(session: Session) -> list[str]:
    from services.shared.db.models import IngestionJob

    return list(
        session.scalars(
            select(IngestionJob.id)
            .where(IngestionJob.status == "completed")
            .order_by(IngestionJob.started_at, IngestionJob.id)
        )
    )


def _build_config_version(profile: str | None) -> str:
    return "weekly-bootstrap-v1" if not profile else f"weekly-bootstrap-v1:{profile}"


def _validate_inputs(state: WeeklyRunState) -> WeeklyRunState:
    if not state["input_job_ids"]:
        raise RuntimeError("No completed ingestion jobs were found for the weekly run.")
    return {
        **state,
        "input_job_count": len(state["input_job_ids"]),
    }


def _finalize_success(state: WeeklyRunState) -> WeeklyRunState:
    return {
        **state,
        "status": "completed",
        "error_summary": None,
    }


def _extract_features(session: Session, state: WeeklyRunState) -> WeeklyRunState:
    summary: FeatureExtractionSummary = extract_latest_snapshot_signals(session)
    session.commit()

    if summary.latest_snapshots == 0:
        raise RuntimeError("No product snapshots were available for feature extraction.")

    return {
        **state,
        "products_considered": summary.products_considered,
        "latest_snapshots": summary.latest_snapshots,
        "signals_created": summary.signals_created,
    }


def _run_trend_agent(session: Session, state: WeeklyRunState) -> WeeklyRunState:
    week_start = date.fromisoformat(state["week_start"])
    results = evaluate_trend_candidates(session, week_start)
    if not results:
        raise RuntimeError("Trend Agent could not score any products from the current signals.")

    serialized_results = [result.as_payload() for result in results]
    return {
        **state,
        "trend_products_scored": len(results),
        "trend_top_score": max(result.normalized_score for result in results),
        "trend_results": serialized_results,
    }


def _run_viral_potential_agent(session: Session, state: WeeklyRunState) -> WeeklyRunState:
    week_start = date.fromisoformat(state["week_start"])
    results = evaluate_viral_potential_candidates(session, week_start)
    if not results:
        raise RuntimeError(
            "Viral Potential Agent could not score any products from the current signals."
        )

    serialized_results = [result.as_payload() for result in results]
    return {
        **state,
        "viral_products_scored": len(results),
        "viral_top_score": max(result.normalized_score for result in results),
        "viral_results": serialized_results,
    }


def _run_creator_accessibility_agent(session: Session, state: WeeklyRunState) -> WeeklyRunState:
    week_start = date.fromisoformat(state["week_start"])
    results = evaluate_creator_accessibility_candidates(session, week_start)
    if not results:
        raise RuntimeError(
            "Creator Accessibility Agent could not score any products from the current signals."
        )

    serialized_results = [result.as_payload() for result in results]
    return {
        **state,
        "creator_products_scored": len(results),
        "creator_top_score": max(result.normalized_score for result in results),
        "creator_results": serialized_results,
    }


def _aggregate_scores(session: Session, state: WeeklyRunState) -> WeeklyRunState:
    week_start = date.fromisoformat(state["week_start"])
    aggregated_scores = persist_aggregated_scores(
        session,
        run_id=state["run_id"],
        agent_inputs=load_trend_inputs(session, week_start=week_start),
        trend_results=state["trend_results"],
        viral_results=state["viral_results"],
        creator_results=state["creator_results"],
        config_version=state["config_version"],
    )
    session.commit()

    if not aggregated_scores:
        raise RuntimeError("Final score aggregation could not persist any product scores.")

    top_score = max(
        aggregated_scores,
        key=lambda aggregated_score: (
            aggregated_score.final_score,
            aggregated_score.product_id,
        ),
    )
    return {
        **state,
        "final_scores_persisted": len(aggregated_scores),
        "top_final_score": float(top_score.final_score),
        "top_classification": top_score.classification,
    }


def _generate_content_angles(session: Session, state: WeeklyRunState) -> WeeklyRunState:
    if not LLM_AVAILABLE:
        return state

    week_start = date.fromisoformat(state["week_start"])
    generate_angles_for_top_products(
        session,
        run_id=state["run_id"],
        week_start=week_start,
        limit=20,
    )
    session.commit()
    return state


def _estimate_saturation(session: Session, state: WeeklyRunState) -> WeeklyRunState:
    week_start = date.fromisoformat(state["week_start"])
    estimates = estimate_saturation_for_top_products(
        session,
        run_id=state["run_id"],
        week_start=week_start,
        limit=50,
    )
    if estimates:
        session.commit()
    return {
        **state,
        "saturation_estimates": len(estimates),
    }


def execute_pipeline(
    session: Session,
    week_start: date,
    profile: str | None,
    *,
    run_id: str | None = None,
    config_version: str | None = None,
    input_job_ids: list[str] | None = None,
) -> WeeklyRunState:
    config = PipelineConfig(
        run_id=run_id or str(uuid4()),
        week_start=week_start,
        profile=profile,
        config_version=config_version or _build_config_version(profile),
        input_job_ids=input_job_ids if input_job_ids is not None else _completed_job_ids(session),
    )
    state = build_initial_weekly_run_state(
        run_id=config.run_id,
        week_start=config.week_start,
        profile=config.profile,
        config_version=config.config_version,
        input_job_ids=config.input_job_ids,
    )

    state = _validate_inputs(state)
    state = _extract_features(session, state)
    state = _run_trend_agent(session, state)
    state = _run_viral_potential_agent(session, state)
    state = _run_creator_accessibility_agent(session, state)
    state = _aggregate_scores(session, state)
    state = _estimate_saturation(session, state)
    state = _generate_content_angles(session, state)
    state = _finalize_success(state)
    return cast(WeeklyRunState, state)
