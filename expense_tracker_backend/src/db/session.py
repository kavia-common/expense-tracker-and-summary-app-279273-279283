"""Database engine and session management for the application."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import get_settings

logger = logging.getLogger(__name__)

# Create engine
settings = get_settings()
# If using SQLite, ensure check_same_thread False for multithreaded FastAPI
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, echo=False, future=True, connect_args=connect_args)

# Configure a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


# PUBLIC_INTERFACE
def get_db() -> Generator:
    """Yield a SQLAlchemy session as a FastAPI dependency, with safe cleanup.

    Yields:
        A database session bound to the configured engine.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        try:
            db.close()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to close DB session: %s", exc)


@contextmanager
def db_session() -> Generator:
    """Context manager for non-request session usage (e.g., CLI initialization)."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as exc:  # noqa: BLE001
        session.rollback()
        logger.exception("DB error, rolled back: %s", exc)
        raise
    finally:
        session.close()
