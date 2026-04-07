from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import pytest

from ingestion.__main__ import main as cli_main
from ingestion.clients import ApifyClient, TikTokShopAuthError
from ingestion.config import IngestionConfig
from ingestion.pipeline import IngestionPipeline
from ingestion.scrapers import TikTokVideosScraper
from scoring import ProductSignals
from services.shared.config import ROOT_DIR


def _config(cache_dir: Path) -> IngestionConfig:
    return IngestionConfig(
        apify_token="test-token",
        keywords=["led strip", "mini massager"],
        tiktok_app_key="app-key",
        tiktok_app_secret="app-secret",
        tiktok_auth_code="auth-code",
        max_products_per_keyword=2,
        max_videos_per_keyword=2,
        cache_dir=str(cache_dir),
        days_lookback=30,
    )


def _workspace_tmp_dir(prefix: str) -> Path:
    base_dir = ROOT_DIR / ".tmp"
    base_dir.mkdir(parents=True, exist_ok=True)
    target_dir = base_dir / f"{prefix}-{uuid4().hex}"
    target_dir.mkdir()
    return target_dir


def _raw_product(product_id: str) -> dict[str, object]:
    return {
        "product_id": product_id,
        "title": f"Product {product_id}",
        "category_name": "home",
        "price": {"amount": 10.0, "currency": "BRL"},
        "commission_rate": 0.1,
        "sales_volume_7d": 70,
    }


def _raw_video(author_id: str) -> dict[str, object]:
    return {
        "id": f"video-{author_id}",
        "createTime": 0,
        "author": {"id": author_id, "followerCount": 100},
        "stats": {
            "playCount": 100,
            "diggCount": 50,
            "shareCount": 20,
            "commentCount": 10,
        },
        "desc": "demo",
    }


def _raw_trends() -> list[dict[str, object]]:
    return [
        {"date": "2026-03-13", "value": 10},
        {"date": "2026-03-14", "value": 20},
        {"date": "2026-03-15", "value": 30},
        {"date": "2026-03-16", "value": 40},
        {"date": "2026-03-17", "value": 50},
        {"date": "2026-03-18", "value": 60},
    ]


def test_pipeline_calls_all_three_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = IngestionPipeline(_config(_workspace_tmp_dir("ingestion-pipeline-three-sources")))
    shop_fetch = AsyncMock(return_value=[_raw_product("product-1")])
    videos_fetch = AsyncMock(return_value=[_raw_video("author-1")])
    trends_fetch = AsyncMock(return_value=_raw_trends())
    monkeypatch.setattr(pipeline.shop_scraper, "fetch", shop_fetch)
    monkeypatch.setattr(pipeline.videos_scraper, "fetch", videos_fetch)
    monkeypatch.setattr(pipeline.trends_scraper, "fetch", trends_fetch)

    asyncio.run(pipeline.run(["led strip"]))

    assert shop_fetch.await_count == 1
    assert videos_fetch.await_count == 1
    assert trends_fetch.await_count == 1


def test_pipeline_returns_product_signals_list(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = IngestionPipeline(_config(_workspace_tmp_dir("ingestion-pipeline-signals")))
    monkeypatch.setattr(
        pipeline.shop_scraper, "fetch", AsyncMock(return_value=[_raw_product("product-1")])
    )
    monkeypatch.setattr(
        pipeline.videos_scraper, "fetch", AsyncMock(return_value=[_raw_video("author-1")])
    )
    monkeypatch.setattr(pipeline.trends_scraper, "fetch", AsyncMock(return_value=_raw_trends()))

    signals = asyncio.run(pipeline.run(["led strip"]))

    assert len(signals) == 1
    assert signals[0].product_id == "product-1"
    assert signals[0].sales_velocity == pytest.approx(10.0)
    assert signals[0].google_trend_score == pytest.approx(60.0)


def test_pipeline_continues_on_tiktok_auth_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = IngestionPipeline(_config(_workspace_tmp_dir("ingestion-pipeline-auth-failure")))

    async def auth_failure(keyword: str) -> list[dict[str, object]]:
        del keyword
        raise TikTokShopAuthError("expired")

    monkeypatch.setattr(pipeline.shop_scraper, "fetch", auth_failure)
    monkeypatch.setattr(
        pipeline.videos_scraper, "fetch", AsyncMock(return_value=[_raw_video("author-1")])
    )
    monkeypatch.setattr(pipeline.trends_scraper, "fetch", AsyncMock(return_value=_raw_trends()))

    signals = asyncio.run(pipeline.run(["led strip"]))

    assert signals == []


def test_pipeline_continues_on_pytrends_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = IngestionPipeline(_config(_workspace_tmp_dir("ingestion-pipeline-rate-limit")))
    monkeypatch.setattr(
        pipeline.shop_scraper, "fetch", AsyncMock(return_value=[_raw_product("product-1")])
    )
    monkeypatch.setattr(
        pipeline.videos_scraper, "fetch", AsyncMock(return_value=[_raw_video("author-1")])
    )

    async def trends_failure(keyword: str) -> list[dict[str, object]]:
        del keyword
        raise RuntimeError("429 Too Many Requests")

    monkeypatch.setattr(pipeline.trends_scraper, "fetch", trends_failure)

    signals = asyncio.run(pipeline.run(["led strip"]))

    assert len(signals) == 1
    assert signals[0].google_trend_score == pytest.approx(0.0)


def test_pipeline_concurrent_keyword_processing(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = IngestionPipeline(_config(_workspace_tmp_dir("ingestion-pipeline-concurrency")))
    started: set[str] = set()
    gate = asyncio.Event()

    async def shop_fetch(keyword: str) -> list[dict[str, object]]:
        started.add(keyword)
        if len(started) == 2:
            gate.set()
        await asyncio.wait_for(gate.wait(), timeout=1.0)
        return [_raw_product(keyword)]

    monkeypatch.setattr(pipeline.shop_scraper, "fetch", shop_fetch)
    monkeypatch.setattr(
        pipeline.videos_scraper, "fetch", AsyncMock(return_value=[_raw_video("author-1")])
    )
    monkeypatch.setattr(pipeline.trends_scraper, "fetch", AsyncMock(return_value=_raw_trends()))

    signals = asyncio.run(pipeline.run(["led strip", "mini massager"]))

    assert sorted(signal.product_id for signal in signals) == ["led strip", "mini massager"]


def test_cache_saves_three_separate_entries_per_keyword(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = IngestionPipeline(_config(_workspace_tmp_dir("ingestion-pipeline-cache")))
    monkeypatch.setattr(
        pipeline.shop_scraper, "fetch", AsyncMock(return_value=[_raw_product("product-1")])
    )
    monkeypatch.setattr(
        pipeline.videos_scraper, "fetch", AsyncMock(return_value=[_raw_video("author-1")])
    )
    monkeypatch.setattr(pipeline.trends_scraper, "fetch", AsyncMock(return_value=_raw_trends()))
    raw_calls: list[tuple[str, str]] = []

    def record_raw(keyword: str, source: str, data: list[dict[str, object]]) -> None:
        del data
        raw_calls.append((keyword, source))

    monkeypatch.setattr(pipeline.cache, "save_raw", record_raw)

    asyncio.run(pipeline.run(["led strip"]))

    assert raw_calls == [
        ("led strip", "tiktok_shop"),
        ("led strip", "tiktok_videos"),
        ("led strip", "google_trends"),
    ]


def test_pipeline_uses_cached_product_history_for_days_since_detected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = IngestionPipeline(_config(_workspace_tmp_dir("ingestion-pipeline-days")))
    monkeypatch.setattr(
        pipeline.shop_scraper, "fetch", AsyncMock(return_value=[_raw_product("product-1")])
    )
    monkeypatch.setattr(pipeline.videos_scraper, "fetch", AsyncMock(return_value=[]))
    monkeypatch.setattr(pipeline.trends_scraper, "fetch", AsyncMock(return_value=[]))
    cached_signal = ProductSignals(
        product_id="product-1",
        name="LED Strip",
        category="home",
        price=10.0,
        commission_rate=0.1,
        sales_velocity=1.0,
        google_trend_score=0.0,
        view_growth_7d=0.0,
        view_growth_3d=0.0,
        active_creators=0,
        days_since_detected=5,
        demo_value=0.0,
        visual_transform=0.0,
        hook_clarity=0.0,
    )
    monkeypatch.setattr(pipeline.cache, "load_latest_signals", lambda: [cached_signal])

    signals = asyncio.run(pipeline.run(["led strip"]))

    assert signals[0].days_since_detected == 6


def test_config_requires_tiktok_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APIFY_TOKEN", "secret")
    monkeypatch.setenv("INGESTION_BACKEND", "official")
    monkeypatch.delenv("TIKTOK_APP_KEY", raising=False)
    monkeypatch.delenv("TIKTOK_APP_SECRET", raising=False)

    with pytest.raises(ValueError, match="TIKTOK_APP_KEY"):
        IngestionConfig.from_env()


def test_apify_client_retries_on_server_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] < 3:
            return httpx.Response(500, json={"error": "server"})
        return httpx.Response(200, json={"data": {"id": "run-123"}})

    client = ApifyClient(token="secret-token")
    monkeypatch.setattr(
        client,
        "_build_client",
        lambda: httpx.AsyncClient(
            transport=httpx.MockTransport(handler),
            base_url=client.BASE_URL,
        ),
    )
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())

    run_id = asyncio.run(client.run_actor("actor-id", {"foo": "bar"}))

    assert run_id == "run-123"
    assert attempts["count"] == 3


def test_apify_client_retries_request_timeouts(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise httpx.ReadTimeout("boom", request=request)
        return httpx.Response(200, json={"data": {"id": "run-123"}})

    client = ApifyClient(token="secret-token")
    monkeypatch.setattr(
        client,
        "_build_client",
        lambda: httpx.AsyncClient(
            transport=httpx.MockTransport(handler),
            base_url=client.BASE_URL,
        ),
    )
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())

    run_id = asyncio.run(client.run_actor("actor-id", {"foo": "bar"}))

    assert run_id == "run-123"
    assert attempts["count"] == 3


def test_apify_client_timeout_and_failed_run_do_not_leak_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failed_client = ApifyClient(token="secret-token")
    monkeypatch.setattr(
        failed_client,
        "_build_client",
        lambda: httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json={"data": {"status": "FAILED"}})
            ),
            base_url=failed_client.BASE_URL,
        ),
    )

    with pytest.raises(RuntimeError, match="FAILED") as failed_error:
        asyncio.run(failed_client.wait_for_run("run-1"))

    assert "secret-token" not in str(failed_error.value)

    timeout_client = ApifyClient(token="secret-token", poll_interval=0, timeout=0)
    monkeypatch.setattr(
        timeout_client,
        "_build_client",
        lambda: httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json={"data": {"status": "RUNNING"}})
            ),
            base_url=timeout_client.BASE_URL,
        ),
    )
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())

    with pytest.raises(RuntimeError, match="Timed out") as timeout_error:
        asyncio.run(timeout_client.wait_for_run("run-2"))

    assert "secret-token" not in str(timeout_error.value)


def test_apify_client_request_timeout_does_not_leak_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = ApifyClient(token="secret-token")
    monkeypatch.setattr(
        client,
        "_build_client",
        lambda: httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: (_ for _ in ()).throw(httpx.ReadTimeout("boom", request=request))
            ),
            base_url=client.BASE_URL,
        ),
    )
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())

    with pytest.raises(RuntimeError, match="timed out") as timeout_error:
        asyncio.run(client.run_actor("actor-id", {"foo": "bar"}))

    assert "secret-token" not in str(timeout_error.value)


def test_tiktok_videos_scraper_uses_apidojo_payload_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    client = ApifyClient(token="secret-token")
    run_and_collect = AsyncMock(return_value=[])
    monkeypatch.setattr(client, "run_and_collect", run_and_collect)
    videos = TikTokVideosScraper(client, results_per_page=15)

    asyncio.run(videos.fetch("led strip"))

    assert run_and_collect.await_args is not None
    assert run_and_collect.await_args.args == (
        "apidojo~tiktok-scraper",
        {
            "searchSection": "/search/video",
            "maxItems": 15,
            "region": "BR",
            "keyword": "led strip",
        },
    )


def test_cli_main_generates_output_file(monkeypatch: pytest.MonkeyPatch) -> None:
    output_dir = _workspace_tmp_dir("ingestion-cli-output")
    output_path = output_dir / "signals.json"
    monkeypatch.setenv("APIFY_TOKEN", "secret")
    monkeypatch.setenv("TIKTOK_APP_KEY", "app-key")
    monkeypatch.setenv("TIKTOK_APP_SECRET", "app-secret")
    monkeypatch.setenv("TIKTOK_AUTH_CODE", "auth-code")
    monkeypatch.setenv("INGESTION_KEYWORDS", "led strip")

    async def fake_run(
        self: IngestionPipeline, keywords: list[str] | None = None
    ) -> list[ProductSignals]:
        del self, keywords
        return [
            ProductSignals(
                product_id="product-1",
                name="LED Strip",
                category="home",
                price=10.0,
                commission_rate=0.1,
                sales_velocity=1.0,
                google_trend_score=50.0,
                view_growth_7d=0.2,
                view_growth_3d=0.1,
                active_creators=2,
                days_since_detected=0,
                demo_value=20.0,
                visual_transform=10.0,
                hook_clarity=15.0,
            )
        ]

    monkeypatch.setattr(IngestionPipeline, "run", fake_run)

    exit_code = cli_main(["--output", str(output_path)])

    assert exit_code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload[0]["product_id"] == "product-1"
