"""Database session scaffolding."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from services.shared.config import AppSettings, get_settings


def build_engine(settings: AppSettings | None = None, *, echo: bool = False) -> Engine:
    """Create a SQLAlchemy engine from application settings."""

    active_settings = settings or get_settings()
    return create_engine(active_settings.database_url, pool_pre_ping=True, echo=echo)


def build_session_factory(
    settings: AppSettings | None = None,
    *,
    echo: bool = False,
) -> sessionmaker[Session]:
    """Return a session factory for later domain modules."""

    engine = build_engine(settings=settings, echo=echo)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
