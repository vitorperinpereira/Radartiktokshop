from __future__ import annotations

from services.workers.google_trends import fetch_trend_score


class _FakeSeries:
    def __init__(self, values: list[int]) -> None:
        self._values = values

    @property
    def iloc(self) -> _FakeSeries:
        return self

    def __getitem__(self, index: int) -> int:
        return self._values[index]


class _FakeFrame:
    empty = False

    def __init__(self, keyword: str, values: list[int]) -> None:
        self.keyword = keyword
        self.values = values

    def __contains__(self, item: object) -> bool:
        return item == self.keyword

    def __getitem__(self, item: object) -> _FakeSeries:
        assert item == self.keyword
        return _FakeSeries(self.values)


class _FakeTrendReq:
    def __init__(self, keyword: str, values: list[int]) -> None:
        self.keyword = keyword
        self.values = values

    def build_payload(self, kw_list: list[str], geo: str, timeframe: str) -> None:
        assert kw_list == [self.keyword]
        assert geo == "BR"
        assert timeframe == "now 7-d"

    def interest_over_time(self) -> _FakeFrame:
        return _FakeFrame(self.keyword, self.values)


def test_fetch_trend_score_returns_latest_value(monkeypatch) -> None:
    monkeypatch.setattr(
        "services.workers.google_trends._build_trend_req",
        lambda: _FakeTrendReq("escova alisadora", [12, 42, 65]),
    )

    assert fetch_trend_score("escova alisadora") == 65


def test_fetch_trend_score_returns_none_on_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "services.workers.google_trends._build_trend_req",
        lambda: None,
    )

    assert fetch_trend_score("escova alisadora") is None
