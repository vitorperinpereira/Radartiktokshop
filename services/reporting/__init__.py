"""Weekly report assembly and export logic."""

from services.reporting.builder import (
    ReportCandidate,
    ReportExportResult,
    SnapshotContext,
    build_content_angle,
    build_report_payload,
    export_weekly_report,
)
from services.reporting.read_service import (
    get_product_detail,
    list_pipeline_run_history,
    list_report_history,
    list_weekly_ranking,
)

__all__ = [
    "SnapshotContext",
    "ReportCandidate",
    "ReportExportResult",
    "build_content_angle",
    "build_report_payload",
    "export_weekly_report",
    "list_weekly_ranking",
    "get_product_detail",
    "list_pipeline_run_history",
    "list_report_history",
]
