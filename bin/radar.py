"""CLI control plane for Creator Product Radar."""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ingestion.clients import ApifyClient  # noqa: E402
from ingestion.config import IngestionConfig  # noqa: E402
from ingestion.scrapers.apidojo_products import ApidojoProductScraper  # noqa: E402
from ingestion.scrapers.clockworks_videos import ClockworksVideosScraper  # noqa: E402
from ingestion.scrapers.pro100chok_shop import Pro100chokShopScraper  # noqa: E402
from ingestion.storage import IngestionCache  # noqa: E402
from services.ingestion.adapters import (  # noqa: E402
    load_csv_records,
    load_json_records,
    load_mock_records,
)
from services.ingestion.contracts import IngestionRecord  # noqa: E402
from services.ingestion.service import ingest_records  # noqa: E402
from services.orchestration import execute_pipeline_run  # noqa: E402
from services.reporting import export_weekly_report  # noqa: E402
from services.shared.config import ROOT_DIR, get_settings  # noqa: E402
from services.shared.db.session import build_session_factory  # noqa: E402
from services.shared.health import build_health_payload  # noqa: E402
from services.shared.logging import configure_logging  # noqa: E402


def _parse_keywords(raw_keywords: str | None, *, fallback: list[str]) -> list[str]:
    if raw_keywords is None:
        return list(fallback)
    return [keyword.strip() for keyword in raw_keywords.split(",") if keyword.strip()]


def _coerce_text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):
        for key in ("url", "uri", "src"):
            nested = _coerce_text(value.get(key))
            if nested is not None:
                return nested
        return None
    if isinstance(value, list):
        for item in value:
            nested = _coerce_text(item)
            if nested is not None:
                return nested
        return None

    text = str(value).strip()
    return text or None


def _first_text(raw_product: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        text = _coerce_text(raw_product.get(key))
        if text is not None:
            return text
    return None


def _coerce_decimal(value: object) -> Decimal | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value).strip())
    except (ArithmeticError, InvalidOperation, ValueError):
        return None


def _first_decimal(raw_product: dict[str, Any], *keys: str) -> Decimal | None:
    for key in keys:
        decimal_value = _coerce_decimal(raw_product.get(key))
        if decimal_value is not None:
            return decimal_value
    return None


def _first_int(raw_product: dict[str, Any], *keys: str) -> int | None:
    value = _first_decimal(raw_product, *keys)
    return None if value is None else int(value)


def _coerce_datetime(value: object) -> datetime | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    if isinstance(value, (int, float)):
        timestamp = float(value)
        if timestamp > 1_000_000_000_000:
            timestamp /= 1000
        return datetime.fromtimestamp(timestamp, tz=UTC)

    text = str(value).strip()
    if not text:
        return None
    if text.isdigit():
        return _coerce_datetime(int(text))

    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def _captured_at(raw_product: dict[str, Any]) -> datetime:
    for key in (
        "capturedAt",
        "captured_at",
        "crawlTime",
        "crawl_time",
        "updateTime",
        "updatedAt",
        "createTime",
        "createdAt",
    ):
        parsed = _coerce_datetime(raw_product.get(key))
        if parsed is not None:
            return parsed
    return datetime.now(UTC)


def _dedupe_apify_records(records: list[IngestionRecord]) -> list[IngestionRecord]:
    deduped: dict[tuple[str, str], IngestionRecord] = {}
    for record in records:
        dedupe_key = (
            record.source_name,
            record.source_record_id or record.title,
        )
        deduped.setdefault(dedupe_key, record)
    return list(deduped.values())


def _build_apify_record_for_source(
    raw_product: dict[str, Any],
    *,
    keyword: str,
    source_name: str,
) -> IngestionRecord:
    """Build an IngestionRecord from a raw Apify item for a given source actor."""

    source_record_id = _first_text(raw_product, "productId", "product_id", "itemId", "id")
    title = _first_text(raw_product, "title", "productName", "name", "desc")
    validation_issues: list[str] = []
    if title is None:
        title = f"untitled-{source_name}-{source_record_id or keyword}"
        validation_issues.append("missing_title")

    # Image — each actor uses different field names
    # pro100chok returns imageUrls (array), clockworks nests coverUrl under videoMeta
    _video_meta = raw_product.get("videoMeta") or {}
    image_url = _first_text(
        raw_product,
        "imageUrl",
        "imageUrls",
        "image_url",
        "image",
        "mainImage",
        "cover",
        "coverUrl",
        "thumbnail",
        "thumbnailUrl",
    ) or _coerce_text(_video_meta.get("coverUrl"))
    # Handle nested priceInfo dicts emitted by some actors
    price_raw = raw_product.get("priceInfo") or raw_product
    if isinstance(price_raw, dict) and "salePrice" in price_raw:
        price = _first_decimal(price_raw, "salePrice", "price")
    else:
        price = _first_decimal(raw_product, "price", "salePrice", "minPrice", "currentPrice")

    raw_payload = dict(raw_product)
    raw_payload["apify_keyword"] = keyword
    raw_payload["apify_source"] = source_name

    return IngestionRecord(
        source_name=source_name,
        input_type="apify",
        title=title,
        brand=_first_text(raw_product, "brand", "brandName", "sellerName", "shopName", "seller"),
        category=_first_text(raw_product, "category", "categoryName", "firstCategory"),
        subcategory=_first_text(
            raw_product, "subcategory", "subCategory", "subcategoryName", "secondCategory"
        ),
        image_url=image_url,
        source_record_id=source_record_id,
        captured_at=_captured_at(raw_product),
        price=price,
        orders_estimate=_first_int(
            raw_product, "soldCount", "ordersCount", "orderCount", "salesVolume", "sold"
        ),
        rating=_first_decimal(raw_product, "rating", "ratingAverage", "productRating", "score"),
        commission_rate=_first_decimal(
            raw_product, "commissionRate", "commission", "commissionPercent"
        ),
        country=_first_text(raw_product, "country", "region"),
        raw_payload=raw_payload,
        validation_issues=validation_issues,
    )


# Keep the original for backward-compatibility with tests.
def _build_apify_record(raw_product: dict[str, Any], *, keyword: str) -> IngestionRecord:
    return _build_apify_record_for_source(raw_product, keyword=keyword, source_name="apify")


async def _fetch_keyword_from_scraper(
    scraper_name: str,
    fetch_coro: Any,  # coroutine
) -> tuple[str, list[dict[str, Any]], str | None]:
    """Await one scraper fetch coroutine and return (scraper_name, items, error)."""
    try:
        raw = await fetch_coro
        return scraper_name, raw, None
    except Exception as exc:
        return scraper_name, [], str(exc)


async def _load_apify_records(
    config: IngestionConfig,
    *,
    keywords: list[str],
) -> tuple[list[IngestionRecord], list[str]]:
    """Fetch records from the 3-actor Apify pipeline in parallel per keyword.

    Actors:
      products  – apidojo/tiktok-scraper (product catalog + pricing)
      shop      – pro100chok/tiktok-shop-scraper-usage (shop data, BR proxy)
      videos    – clockworks/tiktok-scraper (video metrics, stored in raw_payload)
    """
    client = ApifyClient(token=config.apify_token)
    cache = IngestionCache(cache_dir=config.cache_dir)

    products_scraper = ApidojoProductScraper(client, max_products=config.max_products_per_keyword)
    shop_scraper = Pro100chokShopScraper(client, max_products=config.max_products_per_keyword)
    videos_scraper = ClockworksVideosScraper(client, max_items=config.max_videos_per_keyword)

    async def fetch_all_for_keyword(
        keyword: str,
    ) -> tuple[str, list[IngestionRecord], str | None]:
        """Run all 3 actors for one keyword concurrently, merge results."""
        tasks = [
            _fetch_keyword_from_scraper("apify_products", products_scraper.fetch(keyword)),
            _fetch_keyword_from_scraper("apify_shop", shop_scraper.fetch(keyword)),
            _fetch_keyword_from_scraper("apify_videos", videos_scraper.fetch(keyword)),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        keyword_records: list[IngestionRecord] = []
        errors: list[str] = []

        for source_name, raw_items, error in results:
            if error:
                errors.append(f"{source_name}: {error}")
                continue
            cache.save_raw(keyword, source_name, raw_items)
            for item in sorted(
                raw_items,
                key=lambda x: (str(x.get("productId", x.get("itemId", x.get("id", "")))),),
            ):
                keyword_records.append(
                    _build_apify_record_for_source(item, keyword=keyword, source_name=source_name)
                )

        # A keyword fails only when ALL 3 sources failed
        if errors and len(errors) == 3:
            return keyword, [], "; ".join(errors)

        return keyword, keyword_records, None

    fetched_groups = await asyncio.gather(*(fetch_all_for_keyword(kw) for kw in keywords))

    records: list[IngestionRecord] = []
    failed_keywords: list[str] = []
    for keyword, keyword_records, error in fetched_groups:
        if error is not None:
            failed_keywords.append(keyword)
        else:
            records.extend(keyword_records)

    return _dedupe_apify_records(records), failed_keywords


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="radar",
        description="CLI-first control plane for Creator Product Radar.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health", help="Print a JSON health payload for the CLI surface.")
    subparsers.add_parser("paths", help="Print important repository paths.")

    db_upgrade = subparsers.add_parser("db-upgrade", help="Apply Alembic migrations.")
    db_upgrade.add_argument("--revision", default="head", help="Alembic revision target.")

    ingest_mock = subparsers.add_parser("ingest-mock", help="Ingest mock source records.")
    ingest_mock.add_argument(
        "--count",
        default=None,
        type=int,
        help="Optional number of mock records. Defaults to the selected profile size.",
    )
    ingest_mock.add_argument(
        "--profile",
        default="smoke",
        choices=["smoke", "demo_weekly", "edge_cases"],
        help="Mock dataset profile.",
    )

    ingest_csv = subparsers.add_parser("ingest-csv", help="Ingest records from a CSV file.")
    ingest_csv.add_argument("--file", required=True, help="Path to the CSV file.")

    ingest_json = subparsers.add_parser("ingest-json", help="Ingest records from a JSON file.")
    ingest_json.add_argument("--file", required=True, help="Path to the JSON file.")

    ingest_apify = subparsers.add_parser(
        "ingest-apify",
        help="Fetch TikTok Shop records from Apify and persist them.",
    )
    ingest_apify.add_argument(
        "--keywords",
        default=None,
        help='Optional comma-separated keyword override, e.g. "led strip,mini massager".',
    )

    weekly_run = subparsers.add_parser("weekly-run", help="Run the weekly pipeline.")
    weekly_run.add_argument(
        "--profile",
        default=None,
        help="Optional seed or execution profile to use for the run.",
    )
    weekly_run.add_argument(
        "--week-start",
        default=None,
        help="Optional ISO date to pin the weekly run window.",
    )

    daily_run = subparsers.add_parser("daily-run", help="Run the daily pipeline.")
    daily_run.add_argument(
        "--profile",
        default=None,
        help="Optional seed or execution profile to use for the run.",
    )
    daily_run.add_argument(
        "--week-start",
        default=None,
        help="Optional ISO date to pin the daily run window.",
    )

    export_report = subparsers.add_parser(
        "export-report",
        help="Build and persist a deterministic weekly report payload.",
    )
    export_report.add_argument(
        "--run-id",
        default=None,
        help="Optional completed pipeline run identifier to export.",
    )
    export_report.add_argument(
        "--week-start",
        default=None,
        help="Optional ISO date to resolve the latest completed run for one week.",
    )
    export_report.add_argument(
        "--limit",
        default=10,
        type=int,
        help="Maximum number of ranked products to include in the report payload.",
    )

    serve_api = subparsers.add_parser("serve-api", help="Run the FastAPI surface.")
    serve_api.add_argument("--host", default=None, help="API host override.")
    serve_api.add_argument("--port", default=None, type=int, help="API port override.")

    serve_dashboard = subparsers.add_parser(
        "serve-dashboard",
        help="Run the Streamlit placeholder dashboard.",
    )
    serve_dashboard.add_argument(
        "--port",
        default=None,
        type=int,
        help="Dashboard port override.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    settings = get_settings()
    configure_logging(settings.log_level)

    if args.command == "health":
        print(json.dumps(build_health_payload(settings, surface="cli"), indent=2))
        return 0

    if args.command == "paths":
        payload = {
            "root_dir": str(ROOT_DIR),
            "api_app": str(ROOT_DIR / "apps" / "api" / "main.py"),
            "dashboard_app": str(ROOT_DIR / "apps" / "dashboard" / "app.py"),
            "compose_file": str(ROOT_DIR / "docker-compose.yml"),
        }
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "db-upgrade":
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", args.revision],
            capture_output=True,
            text=True,
            check=False,
        )
        payload = {
            "status": "ok" if result.returncode == 0 else "error",
            "command": "db-upgrade",
            "revision": args.revision,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
        print(json.dumps(payload, indent=2))
        return result.returncode

    if args.command == "ingest-mock":
        source_name = f"mock-{args.profile}"
        ingestion_summary = ingest_records(
            load_mock_records(count=args.count, source_name=source_name, profile=args.profile),
            source_name=source_name,
            input_type="mock",
            session_factory=build_session_factory(settings=settings),
        )
        print(json.dumps(asdict(ingestion_summary), indent=2))
        return 0

    if args.command == "ingest-csv":
        csv_path = Path(args.file).expanduser().resolve()
        ingestion_summary = ingest_records(
            load_csv_records(csv_path),
            source_name=csv_path.stem,
            input_type="csv",
            session_factory=build_session_factory(settings=settings),
        )
        print(json.dumps(asdict(ingestion_summary), indent=2))
        return 0

    if args.command == "ingest-json":
        json_path = Path(args.file).expanduser().resolve()
        ingestion_summary = ingest_records(
            load_json_records(json_path),
            source_name=json_path.stem,
            input_type="json",
            session_factory=build_session_factory(settings=settings),
        )
        print(json.dumps(asdict(ingestion_summary), indent=2))
        return 0

    if args.command == "ingest-apify":
        try:
            config = IngestionConfig.from_env()
        except ValueError as exc:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "command": "ingest-apify",
                        "error": str(exc),
                    },
                    indent=2,
                )
            )
            return 1

        keywords = _parse_keywords(args.keywords, fallback=config.keywords)
        if not keywords:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "command": "ingest-apify",
                        "error": "Provide `--keywords` or set `INGESTION_KEYWORDS`.",
                    },
                    indent=2,
                )
            )
            return 1

        records, failed_keywords = asyncio.run(_load_apify_records(config, keywords=keywords))
        if not records:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "command": "ingest-apify",
                        "keywords": keywords,
                        "failed_keywords": failed_keywords,
                        "error": "No Apify product records were fetched for persistence.",
                    },
                    indent=2,
                )
            )
            return 1

        ingestion_summary = ingest_records(
            records,
            source_name="apify",
            input_type="apify",
            session_factory=build_session_factory(settings=settings),
        )
        ingest_payload: dict[str, object] = {
            **asdict(ingestion_summary),
            "command": "ingest-apify",
            "keywords": keywords,
            "failed_keywords": failed_keywords,
            "records_fetched": len(records),
        }
        print(json.dumps(ingest_payload, indent=2))
        return 0

    if args.command == "weekly-run":
        weekly_summary = execute_pipeline_run(
            session_factory=build_session_factory(settings=settings),
            week_start=None if args.week_start is None else date.fromisoformat(args.week_start),
            profile=args.profile or settings.seed_profile,
            frequency="weekly",
        )
        print(json.dumps(asdict(weekly_summary), indent=2))
        return 0 if weekly_summary.status == "completed" else 1

    if args.command == "daily-run":
        daily_summary = execute_pipeline_run(
            session_factory=build_session_factory(settings=settings),
            week_start=None if args.week_start is None else date.fromisoformat(args.week_start),
            profile=args.profile or settings.seed_profile,
            frequency="daily",
        )
        print(json.dumps(asdict(daily_summary), indent=2))
        return 0 if daily_summary.status == "completed" else 1

    if args.command == "export-report":
        session_factory = build_session_factory(settings=settings)
        try:
            with session_factory() as session:
                report_summary = export_weekly_report(
                    session,
                    run_id=args.run_id,
                    week_start=(
                        None if args.week_start is None else date.fromisoformat(args.week_start)
                    ),
                    limit=args.limit,
                    timezone=settings.report_timezone,
                )
        except (RuntimeError, ValueError) as exc:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "command": "export-report",
                        "error": str(exc),
                    },
                    indent=2,
                )
            )
            return 1

        # Write JSON cache so ranking API can serve entries from this report
        week_label = report_summary.report_payload.get("week_label", "unknown")
        cache_path = ROOT_DIR / ".cache" / "ranking"
        cache_path.mkdir(parents=True, exist_ok=True)
        cache_file = cache_path / f"ranking_{week_label}.json"
        with open(cache_file, "w", encoding="utf-8") as _f:
            json.dump(report_summary.report_payload, _f, indent=2, default=str)

        print(json.dumps(asdict(report_summary), indent=2))
        return 0

    if args.command == "serve-api":
        import uvicorn

        uvicorn.run(
            "apps.api.main:app",
            host=args.host or settings.api_host,
            port=args.port or settings.api_port,
            reload=False,
        )
        return 0

    if args.command == "serve-dashboard":
        dashboard_app = ROOT_DIR / "apps" / "dashboard" / "app.py"
        dashboard_process = subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(dashboard_app),
                "--server.port",
                str(args.port or settings.dashboard_port),
                "--server.headless",
                "true",
            ],
            check=False,
        )
        return dashboard_process.returncode

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
