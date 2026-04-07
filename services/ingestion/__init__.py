"""Source adapters, normalization, and ingestion flows."""

from services.ingestion.contracts import IngestionRecord, IngestionSummary
from services.ingestion.service import ingest_records

__all__ = ["IngestionRecord", "IngestionSummary", "ingest_records"]
