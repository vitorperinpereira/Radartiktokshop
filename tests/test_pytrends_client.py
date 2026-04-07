from __future__ import annotations

import time

import pytest

from ingestion.clients.pytrends_client import GoogleTrendsClient
from ingestion.transformers.trends_transformer import compute_trend_signal


class _FakeSeries:
    def __init__(self, pairs: list[tuple[str, int]]) -> None:
        self._pairs = pairs

    def items(self) -> list[tuple[str, int]]:
        return self._pairs


class _FakeFrame:
    def __init__(self, keyword: str, pairs: list[tuple[str, int]]) -> None:
        self.empty = False
        self._keyword = keyword
        self._pairs = pairs

    def __contains__(self, item: object) -> bool:
        return item == self._keyword

    def __getitem__(self, item: object) -> _FakeSeries:
        assert item == self._keyword
        return _FakeSeries(self._pairs)


class _FakeTrendReq:
    def __init__(self, keyword: str, pairs: list[tuple[str, int]]) -> None:
        self.keyword = keyword
        self.pairs = pairs

    def build_payload(self, kw_list: list[str], timeframe: str, geo: str) -> None:
        assert kw_list == [self.keyword]
        assert geo == "BR"
        assert timeframe == "now 7-d"

    def interest_over_time(self) -> _FakeFrame:
        return _FakeFrame(self.keyword, self.pairs)


def test_get_interest_over_time_returns_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    client = GoogleTrendsClient()
    monkeypatch.setattr(
        client,
        "_build_trend_req",
        lambda: _FakeTrendReq("led strip", [("2026-03-17", 42), ("2026-03-18", 65)]),
    )

    payload = client.get_interest_over_time("led strip")

    assert payload == {"2026-03-17": 42, "2026-03-18": 65}


def test_returns_empty_dict_on_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    class RateLimitError(Exception):
        pass

    client = GoogleTrendsClient()

    class _RateLimitedTrendReq:
        def build_payload(self, kw_list: list[str], timeframe: str, geo: str) -> None:
            del kw_list, timeframe, geo

        def interest_over_time(self) -> _FakeFrame:
            raise RateLimitError("429 Too Many Requests")

    monkeypatch.setattr(client, "_build_trend_req", lambda: _RateLimitedTrendReq())
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

    assert client.get_interest_over_time("led strip") == {}


def test_compute_trend_signal_empty_list_defaults_to_zeros() -> None:
    signal = compute_trend_signal([])

    assert signal.google_trend_score == 0.0
    assert signal.trend_velocity == 1.0
    assert signal.is_accelerating is False


def test_compute_trend_signal_detects_acceleration() -> None:
    signal = compute_trend_signal(
        [
            {"date": "1", "value": 10},
            {"date": "2", "value": 10},
            {"date": "3", "value": 10},
            {"date": "4", "value": 30},
            {"date": "5", "value": 40},
            {"date": "6", "value": 50},
        ]
    )

    assert signal.is_accelerating is True
    assert signal.google_trend_score == 50.0


def test_trend_velocity_calculation_correct() -> None:
    signal = compute_trend_signal(
        [
            {"date": "1", "value": 10},
            {"date": "2", "value": 20},
            {"date": "3", "value": 30},
            {"date": "4", "value": 20},
            {"date": "5", "value": 30},
            {"date": "6", "value": 40},
        ]
    )

    assert signal.trend_velocity == 1.5
