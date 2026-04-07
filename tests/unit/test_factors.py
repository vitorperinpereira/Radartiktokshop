from __future__ import annotations

import pytest

from scoring import default_params, f_opportunity, f_price


def test_f_price_handles_center_tail_zero_and_negative_inputs() -> None:
    params = default_params()

    assert f_price(25.0, params) == pytest.approx(100.0)
    assert f_price(0.0, params) < 20.0
    assert f_price(-5.0, params) >= 0.0


def test_f_opportunity_handles_sweet_spot_tail_and_negative_inputs() -> None:
    params = default_params()

    assert f_opportunity(0.0, params) == pytest.approx(0.0)
    assert f_opportunity(10.0, params) == pytest.approx(100.0)
    assert 50.0 <= f_opportunity(5.0, params) <= 80.0
    assert f_opportunity(100.0, params) < 10.0
    assert f_opportunity(-1.0, params) == pytest.approx(0.0)
