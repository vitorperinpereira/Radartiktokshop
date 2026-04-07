"""Available ingestion adapters."""

from services.ingestion.adapters.creator_extractor import (
    extract_creators_from_video_payload,
    persist_creators,
)
from services.ingestion.adapters.csv_adapter import load_csv_records
from services.ingestion.adapters.json_adapter import load_json_records
from services.ingestion.adapters.mock_adapter import load_mock_records

__all__ = [
    "extract_creators_from_video_payload",
    "persist_creators",
    "load_csv_records",
    "load_json_records",
    "load_mock_records",
]
