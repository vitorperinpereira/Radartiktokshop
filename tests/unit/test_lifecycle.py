from __future__ import annotations

from scoring import classify_lifecycle


def test_classify_lifecycle_covers_the_requested_states() -> None:
    assert (
        classify_lifecycle(growth_7d=300, active_creators=5, days_since_detected=7) == "EMERGENTE"
    )
    assert (
        classify_lifecycle(growth_7d=600, active_creators=20, days_since_detected=10)
        == "ACELERANDO"
    )
    assert (
        classify_lifecycle(growth_7d=-10, active_creators=90, days_since_detected=30) == "SATURADO"
    )


def test_classify_lifecycle_handles_edge_cases() -> None:
    assert classify_lifecycle(growth_7d=0, active_creators=0, days_since_detected=0) == "EMERGENTE"
    assert (
        classify_lifecycle(growth_7d=250, active_creators=40, days_since_detected=12, growth_3d=200)
        == "PICO"
    )
