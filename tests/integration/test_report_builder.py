from datetime import date
from typing import cast
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from services.ingestion.adapters.mock_adapter import load_mock_records
from services.ingestion.service import ingest_records
from services.orchestration import execute_weekly_run
from services.reporting import export_weekly_report
from services.shared.config import ROOT_DIR, AppSettings
from services.shared.db import Base, ContentAngle, Report, build_engine, build_session_factory


def _build_session_factory() -> tuple[AppSettings, sessionmaker[Session]]:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    db_path = temp_dir / f"report-builder-{uuid4().hex}.sqlite3"
    settings = AppSettings(database_url=f"sqlite+pysqlite:///{db_path.as_posix()}")
    engine = build_engine(settings=settings)
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(settings=settings)
    return settings, session_factory


def test_export_weekly_report_persists_report_and_content_angles() -> None:
    settings, session_factory = _build_session_factory()

    ingest_records(
        load_mock_records(profile="smoke", count=2),
        source_name="mock-smoke",
        input_type="mock",
        session_factory=session_factory,
    )
    weekly_summary = execute_weekly_run(
        session_factory=session_factory,
        week_start=date(2026, 3, 9),
        profile="smoke",
    )

    with session_factory() as session:
        report_summary = export_weekly_report(
            session,
            run_id=weekly_summary.run_id,
            limit=2,
            timezone=settings.report_timezone,
        )

    assert report_summary.status == "draft"
    assert report_summary.item_count == 2
    assert "methodology_disclaimer" in report_summary.report_payload
    assert "data_freshness" in report_summary.report_payload
    summary = cast(dict[str, object], report_summary.report_payload["summary"])
    assert summary["item_count"] == 2

    with session_factory() as session:
        reports = session.scalars(select(Report)).all()
        content_angles = session.scalars(
            select(ContentAngle).order_by(ContentAngle.product_id)
        ).all()

    assert len(reports) == 1
    assert reports[0].run_id == weekly_summary.run_id
    persisted_items = cast(list[dict[str, object]], reports[0].report_payload["items"])
    assert persisted_items[0]["rank"] == 1
    assert persisted_items[0]["lifecycle_phase"] is not None
    assert persisted_items[0]["opportunity_window_days"] is not None
    assert isinstance(persisted_items[0]["content_angles"], list)
    assert isinstance(persisted_items[0]["summary_text"], str)
    assert len(content_angles) > 0
    assert all(angle.hook_text for angle in content_angles)
    assert all(angle.supporting_rationale for angle in content_angles)

    with session_factory() as session:
        second_export = export_weekly_report(
            session,
            run_id=weekly_summary.run_id,
            limit=2,
            timezone=settings.report_timezone,
        )

    assert second_export.report_id == report_summary.report_id

    with session_factory() as session:
        assert len(session.scalars(select(Report)).all()) == 1
        assert len(session.scalars(select(ContentAngle)).all()) > 0


def test_export_weekly_report_defaults_to_latest_completed_run() -> None:
    settings, session_factory = _build_session_factory()

    ingest_records(
        load_mock_records(profile="smoke", count=2),
        source_name="mock-smoke",
        input_type="mock",
        session_factory=session_factory,
    )
    execute_weekly_run(
        session_factory=session_factory,
        week_start=date(2026, 3, 9),
        profile="smoke",
    )
    latest_summary = execute_weekly_run(
        session_factory=session_factory,
        week_start=date(2026, 3, 16),
        profile="smoke",
    )

    with session_factory() as session:
        report_summary = export_weekly_report(
            session,
            timezone=settings.report_timezone,
        )

    assert report_summary.run_id == latest_summary.run_id
    assert report_summary.week_start == "2026-03-16"


def test_export_weekly_report_fails_when_completed_runs_are_missing() -> None:
    settings, session_factory = _build_session_factory()

    with session_factory() as session:
        with pytest.raises(RuntimeError, match="No completed pipeline runs were found"):
            export_weekly_report(
                session,
                timezone=settings.report_timezone,
            )
