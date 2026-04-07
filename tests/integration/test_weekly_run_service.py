from datetime import date
from uuid import uuid4

from sqlalchemy import select

from services.ingestion.adapters.mock_adapter import load_mock_records
from services.ingestion.service import ingest_records
from services.orchestration import execute_weekly_run
from services.shared.config import ROOT_DIR, AppSettings
from services.shared.db import IngestionJob, PipelineRun, ProductScore, ProductSignal
from services.shared.db.base import Base
from services.shared.db.session import build_engine, build_session_factory


def test_weekly_run_persists_pipeline_run_and_signals() -> None:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    db_path = temp_dir / f"weekly-run-{uuid4().hex}.sqlite3"
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

    summary = execute_weekly_run(
        session_factory=session_factory,
        week_start=date(2026, 3, 9),
        profile="smoke",
    )

    assert ingestion_summary.status == "completed"
    assert summary.status == "completed"
    assert summary.products_considered == 2
    assert summary.signals_created == 10
    assert summary.input_job_count == 1
    assert summary.trend_products_scored == 2
    assert summary.trend_top_score is not None
    assert summary.viral_products_scored == 2
    assert summary.viral_top_score is not None
    assert summary.creator_products_scored == 2
    assert summary.creator_top_score is not None
    assert summary.final_scores_persisted == 2
    assert summary.top_final_score is not None
    assert summary.top_classification is not None

    with session_factory() as session:
        runs = session.scalars(select(PipelineRun)).all()
        signals = session.scalars(select(ProductSignal)).all()
        jobs = session.scalars(select(IngestionJob)).all()
        scores = session.scalars(
            select(ProductScore).order_by(ProductScore.final_score.desc())
        ).all()

    assert len(runs) == 1
    assert runs[0].status == "completed"
    assert runs[0].week_start.isoformat() == "2026-03-09"
    assert runs[0].input_job_ids == [jobs[0].id]
    assert len(signals) == 10
    assert len(scores) == 2
    assert scores[0].final_score is not None
    assert scores[0].classification is not None
    assert scores[0].explainability_payload["classification"] == scores[0].classification


def test_weekly_run_marks_failed_run_when_inputs_are_missing() -> None:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    db_path = temp_dir / f"weekly-run-failed-{uuid4().hex}.sqlite3"
    settings = AppSettings(database_url=f"sqlite+pysqlite:///{db_path.as_posix()}")

    engine = build_engine(settings=settings)
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(settings=settings)

    summary = execute_weekly_run(
        session_factory=session_factory,
        week_start=date(2026, 3, 9),
        profile="smoke",
    )

    assert summary.status == "failed"
    assert summary.error_summary == "No completed ingestion jobs were found for the weekly run."
    assert summary.trend_products_scored == 0
    assert summary.trend_top_score is None
    assert summary.viral_products_scored == 0
    assert summary.viral_top_score is None
    assert summary.creator_products_scored == 0
    assert summary.creator_top_score is None
    assert summary.final_scores_persisted == 0
    assert summary.top_final_score is None
    assert summary.top_classification is None

    with session_factory() as session:
        runs = session.scalars(select(PipelineRun)).all()
        signals = session.scalars(select(ProductSignal)).all()
        scores = session.scalars(select(ProductScore)).all()

    assert len(runs) == 1
    assert runs[0].status == "failed"
    assert runs[0].error_summary == summary.error_summary
    assert len(signals) == 0
    assert len(scores) == 0
