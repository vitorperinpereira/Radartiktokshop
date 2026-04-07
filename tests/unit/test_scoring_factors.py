from __future__ import annotations

import pytest

from scoring import default_params, f_opportunity, f_price


def test_f_price_matches_the_impulse_buy_band() -> None:
    params = default_params()

    assert f_price(25.0, params) == pytest.approx(100.0)
    assert f_price(10.0, params) == pytest.approx(24.4731337315, rel=1e-6)
    assert f_price(40.0, params) == pytest.approx(24.4731337315, rel=1e-6)


def test_f_opportunity_matches_the_asymmetric_creator_window() -> None:
    params = default_params()

    assert f_opportunity(0.0, params) == pytest.approx(0.0)
    assert f_opportunity(10.0, params) == pytest.approx(100.0)
    assert f_opportunity(5.0, params) == pytest.approx(75.7858283255, rel=1e-6)
    assert f_opportunity(80.0, params) < 10.0
