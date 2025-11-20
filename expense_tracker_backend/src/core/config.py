"""Application configuration and settings management using environment variables.

This module centralizes configuration and provides helpers to access
safe defaults for local development while allowing override via .env.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load .env if present
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Immutable settings loaded from environment variables."""

    app_name: str = os.getenv("APP_NAME", "Expense Tracker API")
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    # DATABASE_URL can be postgres or other; default to SQLite file for simplicity
    database_url: str = os.getenv(
        "DATABASE_URL",
        os.getenv(
            "SQLITE_URL",
            "sqlite:///./data/expense_tracker.db",
        ),
    )
    # CORS
    cors_allow_origins: str = os.getenv("CORS_ALLOW_ORIGINS", "*")
    cors_allow_credentials: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    cors_allow_methods: str = os.getenv("CORS_ALLOW_METHODS", "*")
    cors_allow_headers: str = os.getenv("CORS_ALLOW_HEADERS", "*")
    # API meta
    api_version: str = os.getenv("API_VERSION", "0.1.0")
    # Security / Auth
    csrf_enabled: bool = os.getenv("CSRF_ENABLED", "false").lower() == "true"
    secret_key: Optional[str] = os.getenv("SECRET_KEY")
    access_token_expires_min: int = int(os.getenv("ACCESS_TOKEN_EXPIRES_MIN", "15"))
    refresh_token_expires_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS", "7"))
    refresh_cookie_name: str = os.getenv("REFRESH_COOKIE_NAME", "rt")
    cookie_secure: bool = os.getenv("COOKIE_SECURE", "true").lower() == "true"
    cookie_samesite: str = os.getenv("COOKIE_SAMESITE", "lax").lower()


def get_settings() -> Settings:
    """Return singleton settings instance."""
    # Simple memoization without global mutation
    if not hasattr(get_settings, "_instance"):
        setattr(get_settings, "_instance", Settings())
    return getattr(get_settings, "_instance")  # type: ignore[attr-defined]


def configure_logging(level_name: Optional[str] = None) -> None:
    """Configure root logging based on settings or provided level."""
    level_str = (level_name or get_settings().log_level or "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    # Reduce noise from dependencies
    for noisy in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(level)
