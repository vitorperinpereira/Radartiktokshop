import pytest

sqlalchemy = pytest.importorskip("sqlalchemy")

from services.shared.db import Base  # noqa: E402


def test_metadata_can_create_schema_in_sqlite() -> None:
    engine = sqlalchemy.create_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(engine)

    inspector = sqlalchemy.inspect(engine)
    table_names = set(inspector.get_table_names())

    assert "products" in table_names
    assert "pipeline_runs" in table_names
    assert "reports" in table_names
