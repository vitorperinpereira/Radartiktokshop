from __future__ import annotations

from scoring import estimate_opportunity_window, simulate_sir
from scoring.saturation_model import _classify_phase


def test_simulate_sir_progresses_through_expected_phases() -> None:
    trajectory = simulate_sir(
        current_creators=5,
        niche_size=200,
        beta=0.2,
        gamma=0.05,
        days_ahead=30,
    )

    phases = [str(step["phase"]) for step in trajectory]

    assert phases[0] == "EMERGENTE"
    assert "ACELERANDO" in phases
    assert "PICO" in phases or "SATURADO" in phases
    assert estimate_opportunity_window(trajectory) is not None


def test_simulate_sir_handles_zero_beta_and_high_gamma() -> None:
    zero_beta = simulate_sir(
        current_creators=5,
        niche_size=200,
        beta=0.0,
        gamma=0.05,
        days_ahead=10,
    )
    assert max(float(step["active_creators"]) for step in zero_beta) <= 5.0

    high_gamma = simulate_sir(
        current_creators=25,
        niche_size=200,
        beta=0.12,
        gamma=0.9,
        days_ahead=10,
    )
    assert float(high_gamma[-1]["active_creators"]) < float(high_gamma[0]["active_creators"])
    assert float(high_gamma[-1]["active_creators"]) < 1.0


def test_classify_phase_covers_edge_states() -> None:
    assert _classify_phase(5.0, 200.0, 0.4) == "EMERGENTE"
    assert _classify_phase(24.0, 200.0, 2.0) == "ACELERANDO"
    assert _classify_phase(80.0, 200.0, 0.5) == "PICO"
    assert _classify_phase(130.0, 200.0, -1.0) == "SATURADO"
