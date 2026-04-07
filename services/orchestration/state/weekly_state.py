"""Typed state payloads for weekly-run orchestration."""

from __future__ import annotations

from datetime import date
from typing import TypedDict


class WeeklyRunState(TypedDict):
    run_id: str
    week_start: str
    profile: str | None
    config_version: str
    input_job_ids: list[str]
    input_job_count: int
    products_considered: int
    latest_snapshots: int
    signals_created: int
    trend_products_scored: int
    trend_top_score: int | None
    trend_results: list[dict[str, object]]
    viral_products_scored: int
    viral_top_score: int | None
    viral_results: list[dict[str, object]]
    creator_products_scored: int
    creator_top_score: int | None
    creator_results: list[dict[str, object]]
    final_scores_persisted: int
    saturation_estimates: int
    top_final_score: float | None
    top_classification: str | None
    status: str
    error_summary: str | None


def build_initial_weekly_run_state(
    *,
    run_id: str,
    week_start: date,
    profile: str | None,
    config_version: str,
    input_job_ids: list[str],
) -> WeeklyRunState:
    return {
        "run_id": run_id,
        "week_start": week_start.isoformat(),
        "profile": profile,
        "config_version": config_version,
        "input_job_ids": input_job_ids,
        "input_job_count": len(input_job_ids),
        "products_considered": 0,
        "latest_snapshots": 0,
        "signals_created": 0,
        "trend_products_scored": 0,
        "trend_top_score": None,
        "trend_results": [],
        "viral_products_scored": 0,
        "viral_top_score": None,
        "viral_results": [],
        "creator_products_scored": 0,
        "creator_top_score": None,
        "creator_results": [],
        "final_scores_persisted": 0,
        "saturation_estimates": 0,
        "top_final_score": None,
        "top_classification": None,
        "status": "running",
        "error_summary": None,
    }
