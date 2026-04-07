from pytest import MonkeyPatch

from services.shared.config import ROOT_DIR, get_settings


def test_settings_pick_up_environment_override(monkeypatch: MonkeyPatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_NAME", "Bootstrap Test")
    monkeypatch.setenv("DEFAULT_AGENT_COUNT", "5")

    settings = get_settings()

    assert settings.app_name == "Bootstrap Test"
    assert settings.default_agent_count == 5
    assert ROOT_DIR.name == "Tiktok Scrapper"

    get_settings.cache_clear()
