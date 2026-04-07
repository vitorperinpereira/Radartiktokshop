"""Calibration helpers for the standalone deterministic scoring engine."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite

DEFAULT_WEIGHTS: dict[str, float] = {
    "w1": 0.25,
    "w2": 0.20,
    "w3": 0.20,
    "w4": 0.15,
    "w5": 0.20,
}

DEFAULT_BONUS_CAP: float = 1.15


def _coerce_float(value: object, *, field_name: str) -> float:
    """Validate and coerce one numeric override into a float."""

    if isinstance(value, bool):
        raise ValueError(f"`{field_name}` must be numeric.")
    if isinstance(value, (int, float)):
        coerced = float(value)
        if not isfinite(coerced):
            raise ValueError(f"`{field_name}` must be finite.")
        return coerced
    raise ValueError(f"`{field_name}` must be numeric.")


def _validate_non_negative(value: float, *, field_name: str) -> None:
    """Reject negative calibration inputs that would invert scoring behavior."""

    if value < 0.0:
        raise ValueError(f"`{field_name}` must be greater than or equal to 0.")


@dataclass(frozen=True, slots=True)
class ScoringParams:
    """Runtime-tunable parameters used by the scoring formulas.

    Attributes:
        k: Saturation coefficient for the exponential trend curve.
        lambda_: Temporal decay coefficient applied after base score computation.
        alpha: Logistic steepness for the competition curve.
        n0: Logistic inflection point for creator competition saturation.
        beta: Multiplier for the acceleration bonus.
        price_optimal: Center point for the price elasticity curve.
        price_sigma: Spread for the price elasticity curve.
        creator_sweet_spot: Creator count sweet spot for opportunity scoring.
        bonus_cap: Maximum value the acceleration bonus factor can reach (default 1.15).
        weights: Layer-2 aggregation weights keyed as `w1`..`w5`.
    """

    k: float
    lambda_: float
    alpha: float
    n0: float
    beta: float
    price_optimal: float
    price_sigma: float
    creator_sweet_spot: float
    bonus_cap: float = DEFAULT_BONUS_CAP
    weights: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Enforce semantic validation for direct construction and runtime overrides."""

        for field_name in (
            "k",
            "lambda_",
            "alpha",
            "n0",
            "beta",
            "price_optimal",
            "price_sigma",
            "creator_sweet_spot",
            "bonus_cap",
        ):
            field_value = _coerce_float(getattr(self, field_name), field_name=field_name)
            _validate_non_negative(field_value, field_name=field_name)
            object.__setattr__(self, field_name, field_value)

        if not isinstance(self.weights, Mapping):
            raise ValueError("`weights` must be a mapping.")

        expected_weight_keys = set(DEFAULT_WEIGHTS)
        actual_weight_keys = set(self.weights)
        if actual_weight_keys != expected_weight_keys:
            missing = sorted(expected_weight_keys - actual_weight_keys)
            extra = sorted(actual_weight_keys - expected_weight_keys)
            details: list[str] = []
            if missing:
                details.append(f"missing: {', '.join(missing)}")
            if extra:
                details.append(f"extra: {', '.join(extra)}")
            detail_text = "; ".join(details)
            raise ValueError(
                f"`weights` must define exactly {', '.join(sorted(expected_weight_keys))}"
                + (f" ({detail_text})" if detail_text else "")
                + "."
            )

        normalized_weights: dict[str, float] = {}
        total_weight = 0.0
        for key, value in self.weights.items():
            weight_value = _coerce_float(value, field_name=key)
            _validate_non_negative(weight_value, field_name=key)
            normalized_weights[key] = weight_value
            total_weight += weight_value

        if total_weight <= 0.0:
            raise ValueError("`weights` must sum to a positive value.")

        object.__setattr__(self, "weights", normalized_weights)

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> ScoringParams:
        """Build params from runtime overrides layered on top of defaults.

        Unknown keys raise ``ValueError`` so misconfigured overrides fail fast.
        Partial weight overrides are merged into the default `w1`..`w5` map.
        """

        defaults = default_params()
        allowed_keys = {
            "k",
            "lambda_",
            "alpha",
            "n0",
            "beta",
            "price_optimal",
            "price_sigma",
            "creator_sweet_spot",
            "bonus_cap",
            "weights",
        }
        unknown_keys = set(data) - allowed_keys
        if unknown_keys:
            unknown = ", ".join(sorted(unknown_keys))
            raise ValueError(f"Unknown scoring parameter override(s): {unknown}")

        weights = dict(defaults.weights)
        raw_weights = data.get("weights")
        if raw_weights is not None:
            if not isinstance(raw_weights, Mapping):
                raise ValueError("`weights` override must be a mapping.")
            for key, value in raw_weights.items():
                weight_key = str(key)
                if weight_key not in DEFAULT_WEIGHTS:
                    raise ValueError(f"Unknown weight override: {weight_key}")
                weights[weight_key] = _coerce_float(value, field_name=weight_key)

        return cls(
            k=_coerce_float(data.get("k", defaults.k), field_name="k"),
            lambda_=_coerce_float(data.get("lambda_", defaults.lambda_), field_name="lambda_"),
            alpha=_coerce_float(data.get("alpha", defaults.alpha), field_name="alpha"),
            n0=_coerce_float(data.get("n0", defaults.n0), field_name="n0"),
            beta=_coerce_float(data.get("beta", defaults.beta), field_name="beta"),
            price_optimal=_coerce_float(
                data.get("price_optimal", defaults.price_optimal),
                field_name="price_optimal",
            ),
            price_sigma=_coerce_float(
                data.get("price_sigma", defaults.price_sigma),
                field_name="price_sigma",
            ),
            creator_sweet_spot=_coerce_float(
                data.get("creator_sweet_spot", defaults.creator_sweet_spot),
                field_name="creator_sweet_spot",
            ),
            bonus_cap=_coerce_float(
                data.get("bonus_cap", defaults.bonus_cap), field_name="bonus_cap"
            ),
            weights=weights,
        )


def default_params() -> ScoringParams:
    """Return the default calibration values for the standalone engine."""

    return ScoringParams(
        k=0.05,
        lambda_=0.03,
        alpha=0.05,
        n0=80.0,
        beta=0.5,
        price_optimal=25.0,
        price_sigma=12.0,
        creator_sweet_spot=10.0,
        bonus_cap=DEFAULT_BONUS_CAP,
        weights=dict(DEFAULT_WEIGHTS),
    )


def from_dict(data: Mapping[str, object]) -> ScoringParams:
    """Convenience wrapper around :meth:`ScoringParams.from_dict`."""

    return ScoringParams.from_dict(data)
