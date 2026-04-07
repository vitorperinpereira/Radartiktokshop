from datetime import UTC, date, datetime
from typing import cast

import services.agents.runtime.summary_generator as summary_module
from services.reporting import (
    ReportCandidate,
    SnapshotContext,
    build_content_angle,
    build_report_payload,
)


def _candidate(
    *,
    product_id: str,
    title: str,
    category: str | None,
    final_score: float,
    trend_score: float,
    viral_score: float,
    creator_score: float,
    summary: str | None,
    top_positive_signals: list[str],
    latest_snapshot: SnapshotContext | None = None,
    gmv_estimate: float | None = 10000.0,
) -> ReportCandidate:
    return ReportCandidate(
        product_id=product_id,
        title=title,
        brand="Veloura",
        category=category,
        subcategory="Haircare",
        image_url="https://example.com/product.jpg",
        final_score=final_score,
        classification="strong_weekly_bet",
        lifecycle_phase="EMERGENTE",
        trend_score=trend_score,
        viral_potential_score=viral_score,
        creator_accessibility_score=creator_score,
        saturation_penalty=3.0,
        revenue_estimate=120.5,
        summary=summary,
        opportunity_window_days=14,
        google_trends_score=63.0,
        risk_flags=[],
        top_positive_signals=top_positive_signals,
        top_negative_signals=["Demand confidence is still early."],
        evidence_highlights=["snapshot_count=2", "orders_estimate_current=320"],
        latest_snapshot=latest_snapshot,
        gmv_estimate=gmv_estimate,
        gmv_caveat="Estimativa direcional - reposicoes e carrinhos abandonados podem distorcer.",
    )


def test_build_content_angle_uses_dominant_signal_and_stored_reason(monkeypatch) -> None:
    monkeypatch.setattr(summary_module, "LLM_AVAILABLE", False)

    candidate = _candidate(
        product_id="product-1",
        title="Heatless Curling Ribbon",
        category="Beauty",
        final_score=78.8,
        trend_score=72.0,
        viral_score=89.0,
        creator_score=81.0,
        summary="Stored summary for operator review.",
        top_positive_signals=["Product has strong visual demo potential for short-form content."],
    )

    angle = build_content_angle(candidate)

    assert angle.angle_type == "demo_hook"
    assert "Heatless Curling Ribbon" in angle.hook_text
    assert "visual demo potential" in angle.hook_text
    assert angle.supporting_rationale == "Stored summary for operator review."


def test_build_report_payload_shapes_summary_and_fallback_content(monkeypatch) -> None:
    monkeypatch.setattr(summary_module, "LLM_AVAILABLE", False)

    generated_at = datetime(2026, 3, 17, 12, 0, tzinfo=UTC)
    first_candidate = _candidate(
        product_id="product-1",
        title="Heatless Curling Ribbon",
        category="Beauty",
        final_score=78.8,
        trend_score=72.0,
        viral_score=89.0,
        creator_score=81.0,
        summary="Stored summary for operator review.",
        top_positive_signals=["Product has strong visual demo potential for short-form content."],
        latest_snapshot=SnapshotContext(
            captured_at="2026-03-16T09:00:00+00:00",
            price=14.9,
            orders_estimate=320,
            rating=4.8,
            commission_rate=18.0,
            source_name="mock-smoke",
            source_record_id="record-1",
        ),
    )
    second_candidate = _candidate(
        product_id="product-2",
        title="Desk Storage Caddy",
        category="Home",
        final_score=70.2,
        trend_score=68.0,
        viral_score=61.0,
        creator_score=75.0,
        summary=None,
        top_positive_signals=[],
    )

    payload = build_report_payload(
        run_id="run-1",
        week_start=date(2026, 3, 16),
        candidates=[first_candidate, second_candidate],
        timezone="America/Sao_Paulo",
        generated_at=generated_at,
    )

    assert payload["report_version"] == "report-mvp-v1"
    assert payload["generated_at"] == "2026-03-17T09:00:00-03:00"
    assert "methodology_disclaimer" in payload
    assert "data_freshness" in payload
    summary = cast(dict[str, object], payload["summary"])
    items = cast(list[dict[str, object]], payload["items"])
    first_item = items[0]
    second_item = items[1]
    first_content_angle = cast(dict[str, object], first_item["content_angle"])
    first_angles = cast(list[dict[str, object]], first_item["content_angles"])
    first_snapshot = cast(dict[str, object], first_item["latest_snapshot"])
    second_content_angle = cast(dict[str, object], second_item["content_angle"])

    assert summary["item_count"] == 2
    assert summary["category_mix"] == [
        {"category": "Beauty", "count": 1},
        {"category": "Home", "count": 1},
    ]
    assert first_item["rank"] == 1
    assert first_item["lifecycle_phase"] == "EMERGENTE"
    assert first_item["opportunity_window_days"] == 14
    assert first_item["google_trends_validation"] is True
    assert first_content_angle["angle_type"] == "demo_hook"
    assert first_angles
    assert first_snapshot["price"] == 14.9
    assert first_item["gmv_estimate"] == 10000.0
    assert isinstance(first_item["summary_text"], str)
    assert str(first_item["summary_text"]).startswith("Heatless Curling Ribbon")
    assert "reposicoes e carrinhos abandonados" in str(first_item["gmv_caveat"])
    assert second_content_angle["angle_type"] == "accessibility_hook"
    assert "Why Desk Storage Caddy looks approachable" in str(second_content_angle["hook_text"])
    assert str(second_content_angle["supporting_rationale"]).startswith(
        "the current score mix stayed stable"
    )
