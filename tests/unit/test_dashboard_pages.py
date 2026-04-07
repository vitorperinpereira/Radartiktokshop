from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
from types import ModuleType, SimpleNamespace
from typing import Literal

import pandas as pd  # type: ignore[import-untyped]
import pytest

from apps.api.schemas import (
    PipelineRunHistoryItem,
    PipelineRunHistoryResponse,
    ProductDetailResponse,
    ProductMetadata,
    ProductScoreDetail,
    RankingItem,
    RankingResponse,
    SnapshotMetadata,
)


class _StopExecution(RuntimeError):
    """Raised by the fake Streamlit module when a page calls `st.stop()`."""


@dataclass
class _DummyContext:
    calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = field(default_factory=list)

    def __enter__(self) -> _DummyContext:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> Literal[False]:
        return False


class _FakeSidebar:
    def __init__(self, owner: _FakeStreamlit) -> None:
        self._owner = owner
        self.multiselect_return: list[str] = []
        self.checkbox_return = False

    def header(self, *args: object, **kwargs: object) -> None:
        self._owner.record("sidebar.header", *args, **kwargs)

    def multiselect(self, *args: object, **kwargs: object) -> list[str]:
        self._owner.record("sidebar.multiselect", *args, **kwargs)
        return self.multiselect_return

    def checkbox(self, *args: object, **kwargs: object) -> bool:
        self._owner.record("sidebar.checkbox", *args, **kwargs)
        return self.checkbox_return


class _FakeStreamlit(ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
        self.session_state: dict[str, object] = {}
        self.sidebar = _FakeSidebar(self)
        self.selectbox_return: object | None = None
        self.button_return = False
        self.switch_page_calls: list[str] = []
        self.column_config = SimpleNamespace(
            ProgressColumn=lambda *args, **kwargs: ("ProgressColumn", args, kwargs),
            NumberColumn=lambda *args, **kwargs: ("NumberColumn", args, kwargs),
            TextColumn=lambda *args, **kwargs: ("TextColumn", args, kwargs),
        )

    def record(self, name: str, *args: object, **kwargs: object) -> None:
        self.calls.append((name, args, kwargs))

    def set_page_config(self, *args: object, **kwargs: object) -> None:
        self.record("set_page_config", *args, **kwargs)

    def title(self, *args: object, **kwargs: object) -> None:
        self.record("title", *args, **kwargs)

    def markdown(self, *args: object, **kwargs: object) -> None:
        self.record("markdown", *args, **kwargs)

    def caption(self, *args: object, **kwargs: object) -> None:
        self.record("caption", *args, **kwargs)

    def divider(self, *args: object, **kwargs: object) -> None:
        self.record("divider", *args, **kwargs)

    def subheader(self, *args: object, **kwargs: object) -> None:
        self.record("subheader", *args, **kwargs)

    def header(self, *args: object, **kwargs: object) -> None:
        self.record("header", *args, **kwargs)

    def metric(self, *args: object, **kwargs: object) -> None:
        self.record("metric", *args, **kwargs)

    def info(self, *args: object, **kwargs: object) -> None:
        self.record("info", *args, **kwargs)

    def error(self, *args: object, **kwargs: object) -> None:
        self.record("error", *args, **kwargs)

    def warning(self, *args: object, **kwargs: object) -> None:
        self.record("warning", *args, **kwargs)

    def success(self, *args: object, **kwargs: object) -> None:
        self.record("success", *args, **kwargs)

    def dataframe(self, *args: object, **kwargs: object) -> None:
        self.record("dataframe", *args, **kwargs)

    def code(self, *args: object, **kwargs: object) -> None:
        self.record("code", *args, **kwargs)

    def write(self, *args: object, **kwargs: object) -> None:
        self.record("write", *args, **kwargs)

    def json(self, *args: object, **kwargs: object) -> None:
        self.record("json", *args, **kwargs)

    def columns(self, count: int) -> tuple[_DummyContext, ...]:
        self.record("columns", count)
        return tuple(_DummyContext() for _ in range(count))

    def tabs(self, labels: list[str]) -> tuple[_DummyContext, ...]:
        self.record("tabs", tuple(labels))
        return tuple(_DummyContext() for _ in labels)

    def selectbox(self, *args: object, **kwargs: object) -> object | None:
        self.record("selectbox", *args, **kwargs)
        return self.selectbox_return

    def button(self, *args: object, **kwargs: object) -> bool:
        self.record("button", *args, **kwargs)
        return self.button_return

    def switch_page(self, target: str) -> None:
        self.switch_page_calls.append(target)

    def stop(self) -> None:
        raise _StopExecution("st.stop() called")


@pytest.fixture()
def fake_streamlit(monkeypatch: pytest.MonkeyPatch) -> _FakeStreamlit:
    fake = _FakeStreamlit()
    monkeypatch.setitem(sys.modules, "streamlit", fake)
    return fake


def _reload_page(module_name: str) -> ModuleType:
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


def _ranking_response() -> RankingResponse:
    return RankingResponse(
        week_start="2026-03-09",
        count=2,
        items=[
            RankingItem(
                product_id="product-1",
                run_id="run-1",
                week_start="2026-03-09",
                title="Heatless Curling Ribbon",
                brand="Brand A",
                category="beauty",
                subcategory="hair",
                image_url=None,
                final_score=91.0,
                classification="strong_weekly_bet",
                trend_score=84.0,
                viral_potential_score=90.0,
                creator_accessibility_score=88.0,
                saturation_penalty=1.0,
                revenue_estimate=123.45,
                saturation_risk="Low",
                risk_flags=["fresh_signal"],
                summary="Strong persisted summary.",
            ),
            RankingItem(
                product_id="product-2",
                run_id="run-1",
                week_start="2026-03-09",
                title="Portable Blender Cup",
                brand="Brand B",
                category="fitness",
                subcategory="kitchen",
                image_url=None,
                final_score=72.0,
                classification="watchlist",
                trend_score=61.0,
                viral_potential_score=68.0,
                creator_accessibility_score=75.0,
                saturation_penalty=3.0,
                revenue_estimate=88.0,
                saturation_risk="Medium",
                risk_flags=[],
                summary=None,
            ),
        ],
    )


def _product_detail_response() -> ProductDetailResponse:
    return ProductDetailResponse(
        product=ProductMetadata(
            id="product-2",
            canonical_key="portable-blender-cup",
            title="Portable Blender Cup",
            brand="Brand B",
            category="fitness",
            subcategory="kitchen",
            image_url=None,
            status="active",
        ),
        score=ProductScoreDetail(
            run_id="run-1",
            week_start="2026-03-09",
            trend_score=61.0,
            viral_potential_score=68.0,
            creator_accessibility_score=75.0,
            saturation_penalty=3.0,
            revenue_estimate=88.0,
            final_score=72.0,
            classification="watchlist",
            saturation_risk="Medium",
            risk_flags=["seasonal"],
            explainability_payload={
                "summary": "Detail summary",
                "top_positive_signals": ["good demo"],
                "top_negative_signals": ["some saturation"],
                "explanation": {
                    "summary": "Detail summary",
                    "strengths": ["good demo"],
                    "weaknesses": ["some saturation"],
                    "evidence": ["snapshot evidence"],
                },
                "agent_reasoning": {
                    "trend": {
                        "summary": "Trend is stable.",
                        "strengths": ["fresh"],
                        "weaknesses": ["flat"],
                        "evidence": ["7d growth"],
                        "signal_breakdown": {"views": 12},
                    },
                    "viral_potential": {
                        "summary": "Visuals are strong.",
                        "strengths": ["short demo"],
                        "weaknesses": [],
                        "evidence": ["ugc clips"],
                        "signal_breakdown": {"transform": 9},
                    },
                    "creator_accessibility": {
                        "summary": "Easy for beginners.",
                        "strengths": ["simple hook"],
                        "weaknesses": [],
                        "evidence": ["low creator count"],
                        "signal_breakdown": {"saturation": 2},
                    },
                },
            },
        ),
        latest_snapshot=SnapshotMetadata(
            captured_at="2026-03-09T00:00:00+00:00",
            price=24.0,
            orders_estimate=17,
            rating=4.8,
            commission_rate=0.12,
            source_name="mock-smoke",
            source_record_id="snapshot-1",
        ),
    )


def _pipeline_history_response() -> PipelineRunHistoryResponse:
    return PipelineRunHistoryResponse(
        count=1,
        items=[
            PipelineRunHistoryItem(
                run_id="run-1",
                week_start="2026-03-09",
                status="completed",
                started_at="2026-03-09T00:00:00+00:00",
                finished_at="2026-03-09T00:05:00+00:00",
                duration_seconds=300,
                input_job_ids=["job-1"],
                config_version="smoke",
                error_summary=None,
                scored_products=2,
                top_final_score=91.0,
                top_classification="strong_weekly_bet",
                report_count=1,
            )
        ],
    )


def test_dashboard_landing_surfaces_success_marker_and_metrics(
    fake_streamlit: _FakeStreamlit,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.dashboard import read_adapter

    monkeypatch.setattr(
        read_adapter,
        "load_rankings",
        lambda: SimpleNamespace(error=None, data=_ranking_response()),
    )

    _reload_page("apps.dashboard.app")

    assert ("title", ("📡 Radar de Produtos para Criadores",), {}) in fake_streamlit.calls
    assert (
        "success",
        ("Ranking semanal carregado com sucesso.",),
        {},
    ) in fake_streamlit.calls
    assert any(
        call[0] == "metric" and call[1][0] == "Semana analisada" for call in fake_streamlit.calls
    )
    assert any(
        call[0] == "metric" and call[1][0] == "Produtos pontuados" for call in fake_streamlit.calls
    )


def test_weekly_radar_filters_and_drilldown_handoff(
    fake_streamlit: _FakeStreamlit,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.dashboard import read_adapter

    fake_streamlit.sidebar.multiselect_return = ["beauty"]
    fake_streamlit.sidebar.checkbox_return = False
    fake_streamlit.selectbox_return = "product-1"
    fake_streamlit.button_return = True

    monkeypatch.setattr(
        read_adapter,
        "load_rankings",
        lambda: SimpleNamespace(error=None, data=_ranking_response()),
    )

    _reload_page("apps.dashboard.pages.1_weekly_radar")

    dataframe_calls = [call for call in fake_streamlit.calls if call[0] == "dataframe"]
    assert dataframe_calls
    dataframe = dataframe_calls[0][1][0]
    assert isinstance(dataframe, pd.DataFrame)
    assert list(dataframe["ID do Produto"]) == ["product-1"]
    assert fake_streamlit.session_state["selected_product_id"] == "product-1"
    assert fake_streamlit.session_state["selected_week_start"] == "2026-03-09"
    assert fake_streamlit.switch_page_calls == ["pages/2_product_drilldown.py"]


def test_product_drilldown_uses_session_state_context(
    fake_streamlit: _FakeStreamlit,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.dashboard import read_adapter

    fake_streamlit.session_state["selected_product_id"] = "product-2"
    fake_streamlit.session_state["selected_week_start"] = "2026-03-09"
    fake_streamlit.selectbox_return = "product-2"
    captured_detail_request: dict[str, object] = {}

    monkeypatch.setattr(
        read_adapter,
        "load_rankings",
        lambda: SimpleNamespace(error=None, data=_ranking_response()),
    )

    def _load_product_detail(product_id: str, **kwargs: object) -> SimpleNamespace:
        captured_detail_request["product_id"] = product_id
        captured_detail_request["week_start"] = kwargs.get("week_start")
        return SimpleNamespace(
            error=None,
            missing=False,
            data=_product_detail_response(),
        )

    monkeypatch.setattr(read_adapter, "load_product_detail", _load_product_detail)

    _reload_page("apps.dashboard.pages.2_product_drilldown")

    selectbox_calls = [call for call in fake_streamlit.calls if call[0] == "selectbox"]
    assert selectbox_calls
    assert selectbox_calls[0][2]["index"] == 1
    assert captured_detail_request == {
        "product_id": "product-2",
        "week_start": "2026-03-09",
    }
    assert any(
        call[0] == "metric" and call[1][0] == "Score de Oportunidade"
        for call in fake_streamlit.calls
    )
    assert any(
        call[0] == "metric" and call[1][0] == "Estimativa de Receita"
        for call in fake_streamlit.calls
    )


def test_pipeline_history_page_reads_backend_history(
    fake_streamlit: _FakeStreamlit,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.dashboard import read_adapter

    monkeypatch.setattr(
        read_adapter,
        "load_pipeline_history",
        lambda: SimpleNamespace(error=None, data=_pipeline_history_response()),
    )

    _reload_page("apps.dashboard.pages.3_pipeline_history")

    assert ("success", ("Histórico de pipeline carregado com sucesso.",), {}) in fake_streamlit.calls
    dataframe_calls = [call for call in fake_streamlit.calls if call[0] == "dataframe"]
    assert dataframe_calls
    dataframe = dataframe_calls[0][1][0]
    assert isinstance(dataframe, pd.DataFrame)
    assert list(dataframe["run_id"]) == ["run-1"]


def test_pipeline_history_page_handles_empty_and_error_states(
    fake_streamlit: _FakeStreamlit,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.dashboard import read_adapter

    monkeypatch.setattr(
        read_adapter,
        "load_pipeline_history",
        lambda: SimpleNamespace(
            error=None,
            data=PipelineRunHistoryResponse(count=0, items=[]),
        ),
    )

    with pytest.raises(_StopExecution):
        _reload_page("apps.dashboard.pages.3_pipeline_history")

    assert (
        "info",
        ("Nenhum histórico de pipeline disponível ainda. Execute o fluxo semanal primeiro.",),
        {},
    ) in fake_streamlit.calls

    fake_streamlit.calls.clear()
    monkeypatch.setattr(
        read_adapter,
        "load_pipeline_history",
        lambda: SimpleNamespace(error="pipeline history unavailable", data=None),
    )

    with pytest.raises(_StopExecution):
        _reload_page("apps.dashboard.pages.3_pipeline_history")

    assert ("error", ("pipeline history unavailable",), {}) in fake_streamlit.calls
