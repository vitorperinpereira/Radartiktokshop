"""Standalone deterministic scoring engine for the Creator Product Radar repo."""

from scoring.aggregator import (
    EXPLOSIVE,
    HIGH,
    LOW,
    NICHE,
    WORTH_TEST,
    acceleration_bonus,
    estimated_revenue_signal,
    label_for_score,
    score_batch,
    score_product,
    time_decay,
)
from scoring.calibration import ScoringParams, default_params, from_dict
from scoring.factors import (
    clamp_score,
    f_competition,
    f_opportunity,
    f_price,
    f_revenue,
    f_trend,
    f_viral,
)
from scoring.lifecycle import classify_lifecycle
from scoring.models import ProductScore, ProductSignals
from scoring.saturation_model import estimate_opportunity_window, simulate_sir

__all__ = [
    "EXPLOSIVE",
    "HIGH",
    "LOW",
    "NICHE",
    "ProductScore",
    "ProductSignals",
    "ScoringParams",
    "WORTH_TEST",
    "acceleration_bonus",
    "clamp_score",
    "default_params",
    "estimated_revenue_signal",
    "classify_lifecycle",
    "estimate_opportunity_window",
    "f_competition",
    "f_opportunity",
    "f_price",
    "f_revenue",
    "f_trend",
    "f_viral",
    "from_dict",
    "label_for_score",
    "score_batch",
    "score_product",
    "simulate_sir",
    "time_decay",
]
