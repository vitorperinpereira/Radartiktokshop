from __future__ import annotations

import subprocess
import sys
import textwrap

from services.shared.config import ROOT_DIR


def test_weekly_run_executes_cleanly_when_warnings_are_errors() -> None:
    script = """
from datetime import date
from uuid import uuid4

from services.ingestion.adapters.mock_adapter import load_mock_records
from services.ingestion.service import ingest_records
from services.orchestration import execute_weekly_run
from services.shared.config import ROOT_DIR, AppSettings
from services.shared.db import Base, build_engine, build_session_factory

temp_dir = ROOT_DIR / ".tmp"
temp_dir.mkdir(exist_ok=True)
db_path = temp_dir / f"runtime-compat-{uuid4().hex}.sqlite3"
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
print(summary.status)
"""
    result = subprocess.run(
        [sys.executable, "-W", "error", "-c", textwrap.dedent(script)],
        capture_output=True,
        check=False,
        cwd=ROOT_DIR,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "completed"
