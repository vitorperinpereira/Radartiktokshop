"""Standalone CLI entrypoint for the multi-source ingestion pipeline."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from ingestion.config import IngestionConfig
from ingestion.pipeline import IngestionPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ingestion",
        description="Standalone multi-source ingestion flow that emits ProductSignals.",
    )
    parser.add_argument(
        "--keywords",
        default=None,
        help='Comma-separated keyword override, e.g. "led strip,mini massager".',
    )
    parser.add_argument(
        "--output",
        default="signals.json",
        help="Path for the final ProductSignals JSON output.",
    )
    return parser


def _parse_keywords(raw_keywords: str | None) -> list[str] | None:
    if raw_keywords is None:
        return None
    return [keyword.strip() for keyword in raw_keywords.split(",") if keyword.strip()]


def _print_summary_line(line: str) -> None:
    try:
        print(line)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "ascii"
        fallback = line.encode(encoding, errors="replace").decode(encoding, errors="replace")
        print(fallback)


async def _run_async(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = IngestionConfig.from_env()
    pipeline = IngestionPipeline(config)
    keywords = _parse_keywords(args.keywords)
    signals = await pipeline.run(keywords=keywords)

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([signal.model_dump(mode="json") for signal in signals], indent=2),
        encoding="utf-8",
    )

    effective_keywords = keywords if keywords is not None else config.keywords
    _print_summary_line("Ingestao concluida")
    _print_summary_line(f"[produtos] {len(signals)} produtos coletados")
    _print_summary_line(f"[keywords] {', '.join(effective_keywords)}")
    _print_summary_line(f"[saida] {output_path}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the standalone ingestion CLI."""

    return asyncio.run(_run_async(argv))


if __name__ == "__main__":
    raise SystemExit(main())
