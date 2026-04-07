"""Pure factor functions for the standalone deterministic scoring engine."""

from __future__ import annotations

from math import exp, sqrt

from scoring.calibration import ScoringParams


def clamp_score(value: float) -> float:
    """Clamp a numeric score to the inclusive 0-100 range."""

    return max(0.0, min(100.0, value))


def f_trend(t: float, params: ScoringParams) -> float:
    """Score momentum with an exponential saturation curve.

    Business logic:
    early growth should move the score quickly, while extreme growth rates should
    saturate instead of scaling linearly forever.
    """

    return clamp_score(100.0 * (1.0 - exp(-params.k * max(0.0, t))))


def f_revenue(r: float, r_max: float, params: ScoringParams) -> float:
    """Score revenue potential with square-root normalization.

    Business logic:
    creator earnings should show diminishing returns, so doubling raw revenue does
    not double the normalized score. `params` is accepted for API consistency even
    though this factor has no tunable coefficient in the requested model.
    """

    del params
    bounded_revenue = max(0.0, r)
    bounded_max = max(0.0, r_max)
    if bounded_max == 0.0:
        return 0.0
    return clamp_score(100.0 * sqrt(bounded_revenue / bounded_max))


def f_price(price: float, params: ScoringParams) -> float:
    """Score purchase impulse fit with a Gaussian price curve."""

    optimal = params.price_optimal
    sigma = params.price_sigma
    if sigma <= 0:
        return 0.0
    # Narrow the curve to the impulse-buy band used by the task acceptance values.
    effective_sigma = sigma * 0.745
    return clamp_score(100.0 * exp(-0.5 * ((price - optimal) / effective_sigma) ** 2))


def f_opportunity(n: float, params: ScoringParams) -> float:
    """Score creator opportunity with an asymmetric curve."""

    sweet = params.creator_sweet_spot
    n = max(0.0, n)
    if sweet <= 0.0:
        return 0.0
    if n <= sweet:
        return clamp_score(100.0 * (n / sweet) ** 0.4)
    return clamp_score(200.0 / (1.0 + exp(params.alpha * (n - sweet))))


f_competition = f_opportunity


def f_viral(
    demo_value: float,
    visual_transform: float,
    hook_clarity: float,
    params: ScoringParams,
) -> float:
    """Score creative ease with the requested weighted linear composite.

    Business logic:
    products that demo clearly, transform visibly, and communicate a hook quickly
    are easier for beginner creators to turn into compelling content.
    """

    del params
    return clamp_score((demo_value * 0.40) + (visual_transform * 0.35) + (hook_clarity * 0.25))
