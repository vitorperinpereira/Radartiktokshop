"""Deterministic SIR saturation model used by the MVP scoring layer."""

from __future__ import annotations

from dataclasses import dataclass

SATURATION_THRESHOLD = 0.60


@dataclass(frozen=True, slots=True)
class SIRStep:
    day: int
    susceptible: float
    active_creators: float
    recovered: float
    daily_delta: float
    saturation_ratio: float
    phase: str

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "day": self.day,
            "susceptible": self.susceptible,
            "active_creators": self.active_creators,
            "recovered": self.recovered,
            "daily_delta": self.daily_delta,
            "saturation_ratio": self.saturation_ratio,
            "phase": self.phase,
        }


def _clamp_positive(value: float) -> float:
    return max(0.0, value)


def _classify_phase(P: float, N: float, dP: float) -> str:
    """Classify the current SIR state into the requested lifecycle phases."""

    if N <= 0.0:
        return "SATURADO"

    ratio = max(0.0, P) / N
    if ratio >= SATURATION_THRESHOLD:
        return "SATURADO"
    if ratio >= 0.45 and dP <= 0.0:
        return "SATURADO"
    if ratio >= 0.30 or (ratio >= 0.18 and dP < max(1.0, P * 0.02)):
        return "PICO"
    if ratio >= 0.10 or dP >= max(1.0, P * 0.05):
        return "ACELERANDO"
    return "EMERGENTE"


def simulate_sir(
    current_creators: float,
    niche_size: float,
    beta: float,
    gamma: float,
    days_ahead: int = 30,
) -> list[dict[str, float | int | str]]:
    """Simulate a discrete SIR trajectory for the requested creator niche."""

    if days_ahead < 0:
        raise ValueError("`days_ahead` must be greater than or equal to zero.")

    total_population = max(0.0, niche_size)
    if total_population <= 0.0:
        return []

    susceptible = max(0.0, total_population - max(0.0, current_creators))
    active = min(total_population, max(0.0, current_creators))
    recovered = max(0.0, total_population - susceptible - active)

    trajectory: list[SIRStep] = []
    previous_active = active
    for day in range(days_ahead + 1):
        daily_delta = active - previous_active if day > 0 else 0.0
        phase = _classify_phase(active, total_population, daily_delta)
        trajectory.append(
            SIRStep(
                day=day,
                susceptible=susceptible,
                active_creators=active,
                recovered=recovered,
                daily_delta=daily_delta,
                saturation_ratio=active / total_population if total_population > 0 else 0.0,
                phase=phase,
            )
        )

        previous_active = active
        if day == days_ahead:
            break

        new_infections = beta * susceptible * active / total_population
        recoveries = gamma * active
        delta_active = new_infections - recoveries

        susceptible = _clamp_positive(susceptible - new_infections)
        active = _clamp_positive(active + delta_active)
        recovered = max(0.0, total_population - susceptible - active)

    return [step.as_dict() for step in trajectory]


def estimate_opportunity_window(trajectory: list[dict[str, float | int | str]]) -> int | None:
    """Return the first day on which the niche exceeds 60% saturation."""

    for step in trajectory:
        saturation_ratio = step.get("saturation_ratio")
        if isinstance(saturation_ratio, (int, float)) and saturation_ratio >= SATURATION_THRESHOLD:
            day = step.get("day")
            if isinstance(day, int):
                return day

    if len(trajectory) < 2:
        return None

    last_step = trajectory[-1]
    previous_step = trajectory[-2]
    last_day = last_step.get("day")
    previous_day = previous_step.get("day")
    last_ratio = last_step.get("saturation_ratio")
    previous_ratio = previous_step.get("saturation_ratio")
    if not all(
        isinstance(value, (int, float))
        for value in (last_day, previous_day, last_ratio, previous_ratio)
    ):
        return None

    daily_ratio_growth = float(last_ratio) - float(previous_ratio)
    if daily_ratio_growth <= 0.0:
        return None

    remaining_ratio = SATURATION_THRESHOLD - float(last_ratio)
    projected_days = int(round(float(last_day) + (remaining_ratio / daily_ratio_growth)))
    return max(int(last_day), projected_days)
