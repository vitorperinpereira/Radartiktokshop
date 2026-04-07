"""Report serialization helpers for offline ranking reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from ranking.models import RankingReport

_CSV_COLUMNS = [
    "rank",
    "product_id",
    "name",
    "category",
    "final_score",
    "label",
    "trend_score",
    "revenue_score",
    "competition_score",
    "viral_score",
    "estimated_weekly_commission",
    "days_since_detected",
    "acceleration_bonus",
]


def to_json(report: RankingReport, path: str) -> None:
    """Serialize a ranking report to pretty-printed JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )


def to_csv(report: RankingReport, path: str) -> None:
    """Serialize a ranking report to CSV using the standard library only."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(_CSV_COLUMNS)
        for entry in report.entries:
            writer.writerow(
                [
                    entry.rank,
                    entry.product_id,
                    entry.name,
                    entry.category,
                    entry.final_score,
                    entry.label,
                    entry.trend_score,
                    entry.revenue_score,
                    entry.competition_score,
                    entry.viral_score,
                    entry.estimated_weekly_commission,
                    entry.days_since_detected,
                    entry.acceleration_bonus,
                ]
            )


def from_json(path: str) -> RankingReport:
    """Load a previously exported JSON ranking report back into a model."""

    input_path = Path(path)
    return RankingReport.model_validate_json(input_path.read_text(encoding="utf-8"))
