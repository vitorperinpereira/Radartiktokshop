from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from apps.api.main import create_app
from apps.api.ranking_api import router as offline_ranking_router
from ranking.models import RankingEntry, RankingReport
from services.shared.config import AppSettings


def _build_client() -> TestClient:
    settings = AppSettings(database_url="sqlite+pysqlite:///:memory:")
    return TestClient(create_app(settings))


def _offline_report() -> RankingReport:
    now = datetime.now(UTC)
    return RankingReport(
        report_id="report-1",
        generated_at=now,
        week_label="2026-W12",
        total_products_analyzed=2,
        top_n=2,
        filters_applied={},
        params_used={},
        entries=[
            RankingEntry(
                rank=1,
                product_id="product-1",
                name="Portable Blender Cup",
                category="Kitchen",
                final_score=87.4,
                label="EXPLOSIVE",
                trend_score=82.5,
                revenue_score=49.0,
                competition_score=68.0,
                viral_score=76.3,
                decay_factor=0.95,
                acceleration_bonus=1.15,
                estimated_weekly_commission=201.82,
                days_since_detected=3,
                scored_at=now,
            ),
            RankingEntry(
                rank=2,
                product_id="product-2",
                name="Pet Hair Roller",
                category="Home",
                final_score=58.3,
                label="WORTH_TEST",
                trend_score=45.0,
                revenue_score=19.0,
                competition_score=85.0,
                viral_score=52.0,
                decay_factor=0.95,
                acceleration_bonus=1.0,
                estimated_weekly_commission=141.45,
                days_since_detected=9,
                scored_at=now,
            ),
        ],
    )


def test_offline_ranking_entries_accept_classification_alias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        offline_ranking_router.ranking_service,
        "get_latest_report",
        lambda: _offline_report(),
    )
    client = _build_client()

    response = client.get(
        "/api/ranking/latest/entries",
        params={"classification": "EXPLOSIVE"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["entries"][0]["product_id"] == "product-1"


def test_api_allows_nextjs_local_origin_for_browser_calls() -> None:
    client = _build_client()

    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
