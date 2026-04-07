from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from apps.api.main import create_app
from services.ingestion.adapters.mock_adapter import load_mock_records
from services.ingestion.service import ingest_records
from services.orchestration import execute_weekly_run
from services.reporting import export_weekly_report
from services.shared.config import ROOT_DIR, AppSettings
from services.shared.db import (
    Base,
    ProductScore,
    build_engine,
    build_session_factory,
)


def _build_test_client() -> tuple[TestClient, AppSettings, str]:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    db_path = temp_dir / f"api-read-{uuid4().hex}.sqlite3"
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
    summary = execute_weekly_run(
        session_factory=session_factory,
        week_start=date(2026, 3, 9),
        profile="smoke",
    )

    with session_factory() as session:
        export_weekly_report(
            session,
            run_id=summary.run_id,
            limit=summary.final_scores_persisted,
            timezone=settings.report_timezone,
        )

        top_score = session.execute(
            select(ProductScore).order_by(ProductScore.final_score.desc()).limit(1)
        ).scalar_one()

    return TestClient(create_app(settings)), settings, top_score.product_id


def test_root_and_health_endpoints_remain_available() -> None:
    client, _, _ = _build_test_client()

    root_response = client.get("/")
    health_response = client.get("/health")

    assert root_response.status_code == 200
    assert root_response.json()["status"] == "ok"
    assert health_response.status_code == 200
    assert health_response.json()["surface"] == "api"


def test_rankings_endpoint_reads_persisted_scores_in_order() -> None:
    client, _, _ = _build_test_client()

    response = client.get("/rankings", params={"week_start": "2026-03-09"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["week_start"] == "2026-03-09"
    assert payload["count"] == 2
    assert payload["items"][0]["final_score"] >= payload["items"][1]["final_score"]
    assert payload["items"][0]["classification"] == "strong_weekly_bet"
    assert "lifecycle_phase" in payload["items"][0]
    assert "opportunity_window_days" in payload["items"][0]
    assert "risk_flags" in payload["items"][0]
    assert isinstance(payload["items"][0]["summary_text"], str)


def test_product_detail_endpoint_returns_persisted_breakdown() -> None:
    client, _, product_id = _build_test_client()

    response = client.get(f"/products/{product_id}", params={"week_start": "2026-03-09"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["product"]["id"] == product_id
    assert payload["score"]["classification"] == "strong_weekly_bet"
    assert payload["score"]["final_score"] is not None
    assert "lifecycle_phase" in payload["score"]
    assert "opportunity_window_days" in payload["score"]
    assert "google_trends_score" in payload["score"]
    assert "explainability_payload" in payload["score"]
    assert payload["latest_snapshot"] is not None
    assert isinstance(payload["summary_text"], str)
    assert "content_angles" in payload
    assert isinstance(payload["content_angles"], list)


def test_product_detail_endpoint_returns_not_found_for_missing_product() -> None:
    client, _, _ = _build_test_client()

    response = client.get("/products/missing-product")

    assert response.status_code == 404


def test_pipeline_and_report_history_endpoints_cover_populated_and_empty_states() -> None:
    client, _, product_id = _build_test_client()

    pipeline_history = client.get("/history/pipeline-runs")
    report_history = client.get("/history/reports")

    assert pipeline_history.status_code == 200
    assert pipeline_history.json()["count"] == 1
    assert pipeline_history.json()["items"][0]["scored_products"] == 2
    assert report_history.status_code == 200
    assert report_history.json()["count"] == 1
    assert report_history.json()["items"][0]["status"] == "draft"
    assert report_history.json()["items"][0]["report_payload"]["report_version"] == "report-mvp-v1"
    assert "methodology_disclaimer" in report_history.json()["items"][0]["report_payload"]

    content_angles_response = client.get(f"/products/{product_id}/content-angles")
    assert content_angles_response.status_code == 200
    assert content_angles_response.json()["count"] > 0

    empty_db_path = ROOT_DIR / ".tmp" / f"api-read-empty-{uuid4().hex}.sqlite3"
    empty_settings = AppSettings(database_url=f"sqlite+pysqlite:///{empty_db_path.as_posix()}")
    empty_engine = build_engine(settings=empty_settings)
    Base.metadata.create_all(empty_engine)
    empty_client = TestClient(create_app(empty_settings))

    empty_rankings = empty_client.get("/rankings")
    empty_pipeline_history = empty_client.get("/history/pipeline-runs")
    empty_report_history = empty_client.get("/history/reports")

    assert empty_rankings.status_code == 200
    assert empty_rankings.json() == {"week_start": None, "count": 0, "items": []}
    assert empty_pipeline_history.status_code == 200
    assert empty_pipeline_history.json() == {"count": 0, "items": []}
    assert empty_report_history.status_code == 200
    assert empty_report_history.json() == {"count": 0, "items": []}
