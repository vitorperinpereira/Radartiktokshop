from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from apps.dashboard.read_adapter import (
    available_categories,
    extract_agent_reasoning,
    extract_explanation,
    filter_ranking_items,
    load_pipeline_history,
    load_product_detail,
    load_rankings,
    product_option_label,
    ranking_items_to_dataframe,
)
from services.ingestion.adapters.mock_adapter import load_mock_records
from services.ingestion.service import ingest_records
from services.orchestration import execute_weekly_run
from services.shared.config import ROOT_DIR, AppSettings
from services.shared.db import Base, ProductScore, build_engine, build_session_factory


def _build_dashboard_fixture() -> tuple[sessionmaker[Session], str]:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    db_path = temp_dir / f"dashboard-read-{uuid4().hex}.sqlite3"
    settings = AppSettings(database_url=f"sqlite+pysqlite:///{db_path.as_posix()}")

    engine = build_engine(settings=settings)
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(settings=settings)

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

    with session_factory() as session:
        top_score = session.execute(
            select(ProductScore).order_by(ProductScore.final_score.desc()).limit(1)
        ).scalar_one()

    return session_factory, top_score.product_id


def test_load_rankings_reads_persisted_scores_and_supports_dashboard_filters() -> None:
    session_factory, _ = _build_dashboard_fixture()

    ranking_result = load_rankings(
        session_factory=session_factory,
        week_start="2026-03-09",
    )

    assert ranking_result.error is None
    assert ranking_result.data is not None
    assert ranking_result.data.week_start == "2026-03-09"
    assert ranking_result.data.count == 2
    assert ranking_result.data.items[0].final_score is not None
    assert ranking_result.data.items[1].final_score is not None
    assert ranking_result.data.items[0].final_score >= ranking_result.data.items[1].final_score

    categories = available_categories(ranking_result.data.items)
    filtered_items = filter_ranking_items(
        ranking_result.data.items,
        categories=[categories[0]],
        hide_high_saturation=False,
    )
    assert filtered_items
    assert all((item.category or "Uncategorized") == categories[0] for item in filtered_items)

    forced_high_risk_items = [
        ranking_result.data.items[0].model_copy(update={"saturation_risk": "High"}),
        *ranking_result.data.items[1:],
    ]
    hidden_high_risk_items = filter_ranking_items(
        forced_high_risk_items,
        categories=[],
        hide_high_saturation=True,
    )
    assert all(item.saturation_risk != "High" for item in hidden_high_risk_items)

    dataframe = ranking_items_to_dataframe(ranking_result.data.items)
    assert list(dataframe.columns) == [
        "Product",
        "Product ID",
        "Brand",
        "Category",
        "Classification",
        "Opportunity Score",
        "Trend Score",
        "Viral Score",
        "Accessibility Score",
        "Saturation Risk",
        "Saturation Penalty",
        "Revenue Estimate",
        "Summary",
    ]
    assert dataframe.iloc[0]["Product ID"] == ranking_result.data.items[0].product_id
    assert ranking_result.data.items[0].product_id in product_option_label(
        ranking_result.data.items[0]
    )


def test_load_rankings_covers_empty_and_error_states(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    empty_db_path = ROOT_DIR / ".tmp" / f"dashboard-read-empty-{uuid4().hex}.sqlite3"
    settings = AppSettings(database_url=f"sqlite+pysqlite:///{empty_db_path.as_posix()}")
    empty_engine = build_engine(settings=settings)
    Base.metadata.create_all(empty_engine)
    empty_session_factory = build_session_factory(settings=settings)

    empty_result = load_rankings(session_factory=empty_session_factory)

    assert empty_result.error is None
    assert empty_result.data is not None
    assert empty_result.data.count == 0
    assert empty_result.data.items == []

    def _raise_read_error(*args: object, **kwargs: object) -> dict[str, object]:
        raise RuntimeError("read service unavailable")

    monkeypatch.setattr("apps.dashboard.read_adapter.list_weekly_ranking", _raise_read_error)

    error_result = load_rankings(session_factory=empty_session_factory)

    assert error_result.data is None
    assert error_result.error is not None
    assert "read service unavailable" in error_result.error


def test_load_product_detail_reads_persisted_explainability_and_snapshot_metadata() -> None:
    session_factory, product_id = _build_dashboard_fixture()

    detail_result = load_product_detail(
        product_id,
        session_factory=session_factory,
        week_start="2026-03-09",
    )

    assert detail_result.error is None
    assert detail_result.missing is False
    assert detail_result.data is not None
    assert detail_result.data.product.id == product_id
    assert detail_result.data.score.final_score is not None
    assert detail_result.data.latest_snapshot is not None

    explanation = extract_explanation(detail_result.data)
    assert explanation.summary is not None
    assert explanation.top_positive_signals
    assert explanation.evidence

    agent_reasoning = extract_agent_reasoning(detail_result.data)
    assert agent_reasoning["trend"].summary is not None
    assert agent_reasoning["trend"].signal_breakdown
    assert agent_reasoning["viral_potential"].summary is not None
    assert agent_reasoning["creator_accessibility"].summary is not None


def test_load_product_detail_covers_missing_snapshot_missing_content_not_found_and_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_factory, product_id = _build_dashboard_fixture()
    detail_result = load_product_detail(product_id, session_factory=session_factory)

    assert detail_result.data is not None

    minimal_detail = detail_result.data.model_copy(
        update={
            "score": detail_result.data.score.model_copy(
                update={"explainability_payload": {"agent_reasoning": {"trend": {}}}}
            ),
            "latest_snapshot": None,
        }
    )

    explanation = extract_explanation(minimal_detail)
    agent_reasoning = extract_agent_reasoning(minimal_detail)

    assert explanation.summary is None
    assert explanation.top_positive_signals == []
    assert explanation.evidence == []
    assert minimal_detail.latest_snapshot is None
    assert agent_reasoning["trend"].summary is None
    assert agent_reasoning["viral_potential"].summary is None

    missing_result = load_product_detail("missing-product", session_factory=session_factory)

    assert missing_result.error is None
    assert missing_result.data is None
    assert missing_result.missing is True

    def _raise_read_error(*args: object, **kwargs: object) -> dict[str, object] | None:
        raise RuntimeError("detail service unavailable")

    monkeypatch.setattr("apps.dashboard.read_adapter.get_product_detail", _raise_read_error)

    error_result = load_product_detail(product_id, session_factory=session_factory)

    assert error_result.data is None
    assert error_result.error is not None
    assert "detail service unavailable" in error_result.error


def test_load_pipeline_history_reads_persisted_runs() -> None:
    session_factory, _ = _build_dashboard_fixture()

    history_result = load_pipeline_history(session_factory=session_factory)

    assert history_result.error is None
    assert history_result.data is not None
    assert history_result.data.count == 1
    assert history_result.data.items[0].status == "completed"
    assert history_result.data.items[0].scored_products == 2


def test_load_pipeline_history_covers_empty_and_error_states(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    empty_db_path = ROOT_DIR / ".tmp" / f"dashboard-history-empty-{uuid4().hex}.sqlite3"
    settings = AppSettings(database_url=f"sqlite+pysqlite:///{empty_db_path.as_posix()}")
    empty_engine = build_engine(settings=settings)
    Base.metadata.create_all(empty_engine)
    empty_session_factory = build_session_factory(settings=settings)

    empty_result = load_pipeline_history(session_factory=empty_session_factory)

    assert empty_result.error is None
    assert empty_result.data is not None
    assert empty_result.data.count == 0
    assert empty_result.data.items == []

    def _raise_read_error(*args: object, **kwargs: object) -> dict[str, object]:
        raise RuntimeError("history service unavailable")

    monkeypatch.setattr("apps.dashboard.read_adapter.list_pipeline_run_history", _raise_read_error)

    error_result = load_pipeline_history(session_factory=empty_session_factory)

    assert error_result.data is None
    assert error_result.error is not None
    assert "history service unavailable" in error_result.error
