"""CLI entrypoint for the standalone offline ranking package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ranking.filters import RankingFilters
from ranking.report import to_csv, to_json
from ranking.service import RankingService
from scoring import ProductSignals, default_params


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for offline ranking generation."""

    parser = argparse.ArgumentParser(
        prog="python -m ranking.cli",
        description="Generate offline ranking reports from scored product signals.",
    )
    parser.add_argument("--input", required=True, help="Path to a JSON file of ProductSignals.")
    parser.add_argument("--top", default=50, type=int, help="How many products to keep.")
    parser.add_argument("--min-score", default=0.0, type=float, help="Minimum score filter.")
    parser.add_argument(
        "--max-creators",
        default=None,
        type=int,
        help="Optional cap for active creators.",
    )
    parser.add_argument(
        "--categories",
        default=None,
        help="Optional comma-separated category filter.",
    )
    parser.add_argument(
        "--max-days",
        default=None,
        type=int,
        help="Optional freshness cap in days since detected.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where JSON and CSV outputs should be written.",
    )
    return parser


def _load_products(input_path: Path) -> list[ProductSignals]:
    """Load product signals from a JSON array on disk."""

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Input JSON must contain a list of ProductSignals.")
    return [ProductSignals.model_validate(item) for item in payload]


def _print_console_line(message: str, *, fallback: str | None = None) -> None:
    """Print a line and degrade gracefully when the console cannot encode Unicode."""

    try:
        print(message)
    except UnicodeEncodeError:
        print(message if fallback is None else fallback)


def main(argv: list[str] | None = None) -> int:
    """Execute the offline ranking CLI flow end-to-end."""

    args = build_parser().parse_args(argv)
    products = _load_products(Path(args.input))
    categories = (
        None
        if args.categories is None
        else [category.strip() for category in args.categories.split(",") if category.strip()]
    )
    filters = RankingFilters(
        min_score=args.min_score,
        max_active_creators=args.max_creators,
        categories=categories,
        max_days_since_detected=args.max_days,
    )

    service = RankingService(default_params())
    report = service.generate_ranking(products, top_n=args.top, filters=filters)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"ranking_{report.week_label}.json"
    csv_path = output_dir / f"ranking_{report.week_label}.csv"
    to_json(report, str(json_path))
    to_csv(report, str(csv_path))

    print(
        f"Ranking gerado: {report.total_products_analyzed} produtos analisados, "
        f"{report.top_n} no relat\u00f3rio"
    )
    _print_console_line(
        f"\U0001F4C1 Arquivos salvos em: {output_dir}",
        fallback=f"Arquivos salvos em: {output_dir}",
    )
    _print_console_line("\U0001F3C6 Top 3:", fallback="Top 3:")
    for entry in report.entries[:3]:
        print(f"#{entry.rank} {entry.name} - Score: {entry.final_score:.1f} ({entry.label})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
