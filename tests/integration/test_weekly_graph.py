from datetime import date
from typing import cast
from uuid import uuid4

from services.agents import (
    evaluate_creator_accessibility_candidates,
    evaluate_trend_candidates,
    evaluate_viral_potential_candidates,
)
from services.ingestion.adapters.mock_adapter import load_mock_records
from services.ingestion.service import ingest_records
from services.orchestration import build_initial_weekly_run_state, build_weekly_run_graph
from services.shared.config import ROOT_DIR, AppSettings
from services.shared.db.base import Base
from services.shared.db.session import build_engine, build_session_factory
from services.workers.feature_extraction import extract_latest_snapshot_signals


def test_weekly_graph_executes_and_retries_transient_feature_extraction_failure() -> None:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    db_path = temp_dir / f"weekly-graph-{uuid4().hex}.sqlite3"
    settings = AppSettings(database_url=f"sqlite+pysqlite:///{db_path.as_posix()}")

    engine = build_engine(settings=settings)
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(settings=settings)

    ingestion_summary = ingest_records(
        load_mock_records(profile="smoke", count=2),
        source_name="mock-smoke",
        input_type="mock",
        session_factory=session_factory,
    )

    attempts = {"count": 0}

    def flaky_extractor(session) -> object:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("transient extraction failure")
        return cast(object, extract_latest_snapshot_signals(session))

    graph = build_weekly_run_graph(
        session_factory=session_factory,
        feature_extractor=flaky_extractor,
        trend_evaluator=evaluate_trend_candidates,
        viral_potential_evaluator=evaluate_viral_potential_candidates,
        creator_accessibility_evaluator=evaluate_creator_accessibility_candidates,
    )
    initial_state = build_initial_weekly_run_state(
        run_id="run-graph-1",
        week_start=date(2026, 3, 9),
        profile="smoke",
        config_version="weekly-bootstrap-v1:smoke",
        input_job_ids=[ingestion_summary.job_id],
    )

    final_state = graph.invoke(initial_state)

    assert attempts["count"] == 2
    assert final_state["status"] == "completed"
    assert final_state["input_job_count"] == 1
    assert final_state["latest_snapshots"] == 2
    assert final_state["signals_created"] == 10
    assert final_state["trend_products_scored"] == 2
    assert final_state["trend_top_score"] is not None
    assert final_state["viral_products_scored"] == 2
    assert final_state["viral_top_score"] is not None
    assert final_state["creator_products_scored"] == 2
    assert final_state["creator_top_score"] is not None
    assert final_state["final_scores_persisted"] == 2
    assert final_state["top_final_score"] is not None
    assert final_state["top_classification"] in {
        "breakout_candidate",
        "strong_weekly_bet",
        "test_selectively",
        "watchlist_only",
        "low_priority",
    }
