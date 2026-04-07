from __future__ import annotations

from math import inf, nan

import pytest

from scoring import ScoringParams, default_params, from_dict


def test_from_dict_rejects_negative_runtime_overrides() -> None:
    with pytest.raises(ValueError, match="beta"):
        from_dict({"beta": -1.0})

    with pytest.raises(ValueError, match="lambda_"):
        from_dict({"lambda_": -0.1})


def test_from_dict_rejects_invalid_weight_shapes() -> None:
    with pytest.raises(ValueError, match="w1"):
        from_dict({"weights": {"w1": -0.10}})

    with pytest.raises(ValueError, match="weights"):
        ScoringParams(
            k=default_params().k,
            lambda_=default_params().lambda_,
            alpha=default_params().alpha,
            n0=default_params().n0,
            beta=default_params().beta,
            price_optimal=default_params().price_optimal,
            price_sigma=default_params().price_sigma,
            creator_sweet_spot=default_params().creator_sweet_spot,
            bonus_cap=default_params().bonus_cap,
            weights={"w1": 0.30, "w2": 0.20, "w3": 0.20, "w4": 0.15},
        )


@pytest.mark.parametrize("invalid_value", [inf, nan])
def test_direct_construction_rejects_non_finite_coefficients(invalid_value: float) -> None:
    with pytest.raises(ValueError, match="k"):
        ScoringParams(
            k=invalid_value,
            lambda_=default_params().lambda_,
            alpha=default_params().alpha,
            n0=default_params().n0,
            beta=default_params().beta,
            price_optimal=default_params().price_optimal,
            price_sigma=default_params().price_sigma,
            creator_sweet_spot=default_params().creator_sweet_spot,
            bonus_cap=default_params().bonus_cap,
            weights=dict(default_params().weights),
        )
