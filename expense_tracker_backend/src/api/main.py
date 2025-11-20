from __future__ import annotations

import logging
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import configure_logging, get_settings

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

openapi_tags = [
    {"name": "Health", "description": "Service health and diagnostics."},
]

app = FastAPI(
    title=settings.app_name,
    description="Backend API for the Expense Tracker application.",
    version=settings.api_version,
    openapi_tags=openapi_tags,
)

# Configure CORS based on env
allow_origins: List[str] = [o.strip() for o in settings.cors_allow_origins.split(",") if o.strip()]
allow_methods: List[str] = [m.strip() for m in settings.cors_allow_methods.split(",") if m.strip()]
allow_headers: List[str] = [h.strip() for h in settings.cors_allow_headers.split(",") if h.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins if allow_origins else ["*"],
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=allow_methods if allow_methods else ["*"],
    allow_headers=allow_headers if allow_headers else ["*"],
)


@app.get("/", tags=["Health"], summary="Health Check")
def health_check():
    """Service health check.

    Returns:
        JSON with a basic message to indicate service availability.
    """
    return {"message": "Healthy"}
