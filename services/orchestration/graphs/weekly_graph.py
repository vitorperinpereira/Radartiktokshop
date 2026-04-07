"""LangGraph weekly-run graph for deterministic bootstrap execution."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from services.agents import (
    AgentScoreResult,
    evaluate_creator_accessibility_candidates,
    evaluate_trend_candidates,
    evaluate_viral_potential_candidates,
    load_trend_inputs,
)
from services.orchestration.state import WeeklyRunState
from services.scoring import persist_aggregated_scores
from services.shared.runtime_compat import install_python314_warning_filters
from services.workers.feature_extraction import (
    FeatureExtractionSummary,
    extract_latest_snapshot_signals,
)

install_python314_warning_filters()

from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.types import RetryPolicy  # noqa: E402

FeatureExtractor = Callable[[Session], FeatureExtractionSummary]
TrendEvaluator = Callable[[Session, date], list[AgentScoreResult]]
ViralPotentialEvaluator = Callable[[Session, date], list[AgentScoreResult]]
CreatorAccessibilityEvaluator = Callable[[Session, date], list[AgentScoreResult]]


def _validate_inputs(state: WeeklyRunState) -> WeeklyRunState:
    input_job_ids = state["input_job_ids"]
    if not input_job_ids:
        raise RuntimeError("No completed ingestion jobs were found for the weekly run.")

    return {
        **state,
        "input_job_count": len(input_job_ids),
    }


def _finalize_success(state: WeeklyRunState) -> WeeklyRunState:
    return {
        **state,
        "status": "completed",
        "error_summary": None,
    }


def build_weekly_run_graph(
    *,
    session_factory: sessionmaker[Session],
    feature_extractor: FeatureExtractor = extract_latest_snapshot_signals,
    trend_evaluator: TrendEvaluator = evaluate_trend_candidates,
    viral_potential_evaluator: ViralPotentialEvaluator = evaluate_viral_potential_candidates,
    creator_accessibility_evaluator: CreatorAccessibilityEvaluator = (
        evaluate_creator_accessibility_candidates
    ),
) -> Any:
    def extract_features(state: WeeklyRunState) -> WeeklyRunState:
        with session_factory() as session:
            summary = feature_extractor(session)
            session.commit()

        if summary.latest_snapshots == 0:
            raise RuntimeError("No product snapshots were available for feature extraction.")

        return {
            **state,
            "products_considered": summary.products_considered,
            "latest_snapshots": summary.latest_snapshots,
            "signals_created": summary.signals_created,
        }

    def run_trend_agent(state: WeeklyRunState) -> WeeklyRunState:
        week_start = date.fromisoformat(state["week_start"])
        with session_factory() as session:
            results = trend_evaluator(session, week_start)

        if not results:
            raise RuntimeError("Trend Agent could not score any products from the current signals.")

        serialized_results = [result.as_payload() for result in results]
        return {
            **state,
            "trend_products_scored": len(results),
            "trend_top_score": max(result.normalized_score for result in results),
            "trend_results": serialized_results,
        }

    def run_viral_potential_agent(state: WeeklyRunState) -> WeeklyRunState:
        week_start = date.fromisoformat(state["week_start"])
        with session_factory() as session:
            results = viral_potential_evaluator(session, week_start)

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

    def run_creator_accessibility_agent(state: WeeklyRunState) -> WeeklyRunState:
        week_start = date.fromisoformat(state["week_start"])
        with session_factory() as session:
            results = creator_accessibility_evaluator(session, week_start)

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

    def run_final_score_aggregation(state: WeeklyRunState) -> WeeklyRunState:
        week_start = date.fromisoformat(state["week_start"])
        with session_factory() as session:
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

    graph = StateGraph(WeeklyRunState)
    graph.add_node("validate_inputs", _validate_inputs)
    graph.add_node(
        "extract_features",
        extract_features,
        retry_policy=RetryPolicy(
            max_attempts=2,
            initial_interval=0.01,
            backoff_factor=1.0,
            max_interval=0.01,
            jitter=False,
            retry_on=(RuntimeError,),
        ),
    )
    graph.add_node("run_trend_agent", run_trend_agent)
    graph.add_node("run_viral_potential_agent", run_viral_potential_agent)
    graph.add_node("run_creator_accessibility_agent", run_creator_accessibility_agent)
    graph.add_node("run_final_score_aggregation", run_final_score_aggregation)
    graph.add_node("finalize_success", _finalize_success)

    graph.add_edge(START, "validate_inputs")
    graph.add_edge("validate_inputs", "extract_features")
    graph.add_edge("extract_features", "run_trend_agent")
    graph.add_edge("run_trend_agent", "run_viral_potential_agent")
    graph.add_edge("run_viral_potential_agent", "run_creator_accessibility_agent")
    graph.add_edge("run_creator_accessibility_agent", "run_final_score_aggregation")
    graph.add_edge("run_final_score_aggregation", "finalize_success")
    graph.add_edge("finalize_success", END)

    return graph.compile(name="weekly_run_bootstrap")
