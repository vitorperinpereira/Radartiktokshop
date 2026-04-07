"""Application settings and path helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]


def _load_dotenv() -> None:
    env_path = ROOT_DIR / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class AppSettings:
    """Central application settings loaded from environment variables."""

    app_name: str = "TikTok Scrapper"
    app_env: str = "development"
    log_level: str = "INFO"
    report_timezone: str = "America/Sao_Paulo"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    dashboard_port: int = 8501

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "tiktok_scrapper"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/tiktok_scrapper"

    model_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"

    seed_profile: str = "smoke"
    default_agent_count: int = 3

    @classmethod
    def from_env(cls) -> AppSettings:
        _load_dotenv()
        return cls(
            app_name=os.getenv("APP_NAME", cls.app_name),
            app_env=os.getenv("APP_ENV", cls.app_env),
            log_level=os.getenv("LOG_LEVEL", cls.log_level),
            report_timezone=os.getenv("REPORT_TIMEZONE", cls.report_timezone),
            api_host=os.getenv("API_HOST", cls.api_host),
            api_port=int(os.getenv("API_PORT", str(cls.api_port))),
            dashboard_port=int(os.getenv("DASHBOARD_PORT", str(cls.dashboard_port))),
            postgres_host=os.getenv("POSTGRES_HOST", cls.postgres_host),
            postgres_port=int(os.getenv("POSTGRES_PORT", str(cls.postgres_port))),
            postgres_db=os.getenv("POSTGRES_DB", cls.postgres_db),
            postgres_user=os.getenv("POSTGRES_USER", cls.postgres_user),
            postgres_password=os.getenv("POSTGRES_PASSWORD", cls.postgres_password),
            database_url=os.getenv("DATABASE_URL", cls.database_url),
            model_provider=os.getenv("MODEL_PROVIDER", cls.model_provider),
            openai_api_key=os.getenv("OPENAI_API_KEY", cls.openai_api_key),
            openai_model=os.getenv("OPENAI_MODEL", cls.openai_model),
            seed_profile=os.getenv("SEED_PROFILE", cls.seed_profile),
            default_agent_count=int(os.getenv("DEFAULT_AGENT_COUNT", str(cls.default_agent_count))),
        )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return a cached settings instance for process-local use."""

    return AppSettings.from_env()
