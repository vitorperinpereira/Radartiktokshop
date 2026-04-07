from __future__ import annotations

import pytest

from scoring import default_params, f_opportunity, f_price, f_revenue, f_trend, f_viral


def test_f_trend_handles_zero_high_and_saturation_inputs() -> None:
    params = default_params()

    assert f_trend(0.0, params) == pytest.approx(0.0)
    assert f_trend(10.0, params) > 39.0
    assert f_trend(100.0, params) == pytest.approx(99.3262053001)


def test_f_opportunity_handles_open_inflection_and_saturated_cases() -> None:
    params = default_params()

    assert f_opportunity(0.0, params) == pytest.approx(0.0)
    assert f_opportunity(10.0, params) == pytest.approx(100.0)
    assert f_opportunity(5.0, params) == pytest.approx(75.7858283255, rel=1e-6)
    assert f_opportunity(80.0, params) < 10.0


def test_f_price_handles_gaussian_center_and_symmetric_tails() -> None:
    params = default_params()

    assert f_price(25.0, params) == pytest.approx(100.0)
    assert f_price(10.0, params) == pytest.approx(24.4731337315, rel=1e-6)
    assert f_price(40.0, params) == pytest.approx(24.4731337315, rel=1e-6)


def test_f_revenue_handles_zero_quarter_and_full_scale_cases() -> None:
    params = default_params()

    assert f_revenue(100.0, 100.0, params) == pytest.approx(100.0)
    assert f_revenue(0.0, 100.0, params) == pytest.approx(0.0)
    assert f_revenue(25.0, 100.0, params) == pytest.approx(50.0)


def test_f_viral_handles_balanced_and_edge_case_inputs() -> None:
    params = default_params()

    assert f_viral(50.0, 50.0, 50.0, params) == pytest.approx(50.0)
    assert f_viral(0.0, 0.0, 0.0, params) == pytest.approx(0.0)
    assert f_viral(100.0, 100.0, 100.0, params) == pytest.approx(100.0)
