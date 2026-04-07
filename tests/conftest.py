from __future__ import annotations

import pytest

import services.agents.runtime.content_angle_generator as content_angle_module
import services.agents.runtime.creator_accessibility_agent as creator_module
import services.agents.runtime.saturation_agent as saturation_module
import services.agents.runtime.summary_generator as summary_module
import services.agents.runtime.viral_potential_agent as viral_module
import services.workers.google_trends as google_trends_module


@pytest.fixture(autouse=True)
def disable_llm_paths(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(summary_module, "LLM_AVAILABLE", False)
    monkeypatch.setattr(content_angle_module, "LLM_AVAILABLE", False)
    monkeypatch.setattr(viral_module, "LLM_AVAILABLE", False)
    monkeypatch.setattr(creator_module, "LLM_AVAILABLE", False)
    monkeypatch.setattr(saturation_module, "LLM_AVAILABLE", False)
    monkeypatch.setattr(google_trends_module, "fetch_trend_score", lambda *args, **kwargs: None)
    viral_module._LLM_CACHE.clear()
    creator_module._LLM_CACHE.clear()
    saturation_module._LLM_CACHE.clear()
    yield
