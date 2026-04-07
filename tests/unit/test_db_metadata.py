import pytest

pytest.importorskip("sqlalchemy")

from services.shared.db import Base  # noqa: E402


def test_expected_tables_are_registered() -> None:
    expected_tables = {
        "products",
        "product_aliases",
        "product_snapshots",
        "creators",
        "creator_products",
        "product_signals",
        "product_scores",
        "content_angles",
        "reports",
        "ingestion_jobs",
        "pipeline_runs",
    }

    assert expected_tables.issubset(Base.metadata.tables.keys())
