import importlib
import json
import os
import subprocess
import sys
from types import ModuleType
from typing import Literal, cast
from uuid import uuid4

from sqlalchemy import select

from services.shared.config import ROOT_DIR, AppSettings, get_settings
from services.shared.db import ContentAngle, Report, build_session_factory


class _SmokeContext:
    def __enter__(self) -> "_SmokeContext":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> Literal[False]:
        return False


class _SmokeStreamlit(ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    def _record(self, name: str, *args: object, **kwargs: object) -> None:
        self.calls.append((name, args, kwargs))

    def set_page_config(self, *args: object, **kwargs: object) -> None:
        self._record("set_page_config", *args, **kwargs)

    def title(self, *args: object, **kwargs: object) -> None:
        self._record("title", *args, **kwargs)

    def markdown(self, *args: object, **kwargs: object) -> None:
        self._record("markdown", *args, **kwargs)

    def metric(self, *args: object, **kwargs: object) -> None:
        self._record("metric", *args, **kwargs)

    def success(self, *args: object, **kwargs: object) -> None:
        self._record("success", *args, **kwargs)

    def caption(self, *args: object, **kwargs: object) -> None:
        self._record("caption", *args, **kwargs)

    def divider(self, *args: object, **kwargs: object) -> None:
        self._record("divider", *args, **kwargs)

    def subheader(self, *args: object, **kwargs: object) -> None:
        self._record("subheader", *args, **kwargs)

    def info(self, *args: object, **kwargs: object) -> None:
        self._record("info", *args, **kwargs)

    def error(self, *args: object, **kwargs: object) -> None:
        self._record("error", *args, **kwargs)

    def warning(self, *args: object, **kwargs: object) -> None:
        self._record("warning", *args, **kwargs)

    def columns(self, count: int) -> tuple[_SmokeContext, ...]:
        self._record("columns", count)
        return tuple(_SmokeContext() for _ in range(count))

    def stop(self) -> None:
        raise AssertionError("st.stop() was called on the success-path smoke")


def _run_cli_json(args: list[str], *, env: dict[str, str]) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, "bin/radar.py", *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return cast(dict[str, object], json.loads(result.stdout))


def test_cli_weekly_run_outputs_json_summary() -> None:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    db_path = temp_dir / f"cli-weekly-run-{uuid4().hex}.sqlite3"
    database_url = f"sqlite+pysqlite:///{db_path.as_posix()}"
    env = {
        **os.environ,
        "DATABASE_URL": database_url,
    }

    migration_payload = _run_cli_json(["db-upgrade"], env=env)
    ingest_payload = _run_cli_json(
        ["ingest-mock", "--profile", "smoke", "--count", "2"],
        env=env,
    )
    weekly_run_payload = _run_cli_json(
        ["weekly-run", "--profile", "smoke", "--week-start", "2026-03-09"],
        env=env,
    )
    daily_run_payload = _run_cli_json(
        ["daily-run", "--profile", "smoke", "--week-start", "2026-03-09"],
        env=env,
    )
    export_payload = _run_cli_json(
        ["export-report", "--week-start", "2026-03-09", "--limit", "2"],
        env=env,
    )

    assert migration_payload["status"] == "ok"
    assert migration_payload["revision"] == "head"
    assert ingest_payload["status"] == "completed"
    assert ingest_payload["records_written"] == 2

    assert weekly_run_payload["status"] == "completed"
    assert weekly_run_payload["week_start"] == "2026-03-09"
    assert weekly_run_payload["input_job_count"] == 1
    assert weekly_run_payload["signals_created"] == 10
    assert weekly_run_payload["trend_products_scored"] == 2
    assert weekly_run_payload["trend_top_score"] is not None
    assert weekly_run_payload["viral_products_scored"] == 2
    assert weekly_run_payload["viral_top_score"] is not None
    assert weekly_run_payload["creator_products_scored"] == 2
    assert weekly_run_payload["creator_top_score"] is not None
    assert weekly_run_payload["final_scores_persisted"] == 2
    assert weekly_run_payload["top_final_score"] is not None
    assert weekly_run_payload["top_classification"] is not None

    assert daily_run_payload["status"] == "completed"
    assert daily_run_payload["week_start"] == "2026-03-09"
    assert daily_run_payload["config_version"].startswith("daily-bootstrap-v1")
    assert daily_run_payload["final_scores_persisted"] == 2

    report_payload = export_payload["report_payload"]
    assert export_payload["status"] == "draft"
    assert export_payload["item_count"] == 2
    assert isinstance(report_payload, dict)
    assert report_payload["report_version"] == "report-mvp-v1"
    assert "methodology_disclaimer" in report_payload
    assert "data_freshness" in report_payload
    assert report_payload["summary"]["item_count"] == 2
    assert len(report_payload["items"]) == 2
    assert isinstance(report_payload["items"][0]["summary_text"], str)
    assert "content_angles" in report_payload["items"][0]
    assert report_payload["items"][0]["lifecycle_phase"] is not None
    session_factory = build_session_factory(settings=AppSettings(database_url=database_url))
    with session_factory() as session:
        reports = session.scalars(select(Report)).all()
        content_angles = session.scalars(select(ContentAngle)).all()

    assert len(reports) == 1
    assert reports[0].status == "draft"
    assert reports[0].report_payload["report_version"] == "report-mvp-v1"
    assert len(content_angles) > 0

    original_database_url = os.environ.get("DATABASE_URL")
    original_streamlit = sys.modules.get("streamlit")
    original_dashboard_app = sys.modules.get("apps.dashboard.app")
    get_settings.cache_clear()
    os.environ["DATABASE_URL"] = database_url
    smoke_streamlit = _SmokeStreamlit()
    sys.modules["streamlit"] = smoke_streamlit
    sys.modules.pop("apps.dashboard.app", None)
    try:
        importlib.import_module("apps.dashboard.app")

        assert ("title", ("📡 Radar de Produtos para Criadores",), {}) in smoke_streamlit.calls
        assert (
            "success",
            ("Ranking semanal carregado com sucesso.",),
            {},
        ) in smoke_streamlit.calls
        assert any(
            call[0] == "metric" and call[1][0] == "Semana analisada"
            for call in smoke_streamlit.calls
        )
        assert any(
            call[0] == "metric" and call[1][0] == "Produtos pontuados"
            for call in smoke_streamlit.calls
        )
    finally:
        if original_streamlit is None:
            sys.modules.pop("streamlit", None)
        else:
            sys.modules["streamlit"] = original_streamlit
        if original_dashboard_app is None:
            sys.modules.pop("apps.dashboard.app", None)
        else:
            sys.modules["apps.dashboard.app"] = original_dashboard_app
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        get_settings.cache_clear()
