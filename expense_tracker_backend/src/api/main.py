from __future__ import annotations

import logging
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import configure_logging, get_settings
from src.api.routers.auth import router as auth_router
from src.api.routers.users import router as users_router
from src.api.routers.categories import router as categories_router
from src.api.routers.transactions import router as transactions_router
from src.api.routers.reports import router as reports_router

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

openapi_tags = [
    {"name": "Health", "description": "Service health and diagnostics."},
    {"name": "Auth", "description": "Authentication endpoints for login, refresh, logout."},
    {"name": "Users", "description": "User profile and management."},
    {"name": "Categories", "description": "Manage expense categories."},
    {"name": "Transactions", "description": "CRUD operations for expenses."},
    {"name": "Reports", "description": "Aggregated reporting endpoints."},
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

@app.get(
    "/health",
    tags=["Health"],
    summary="Health Status",
)
def health_status():
    """Lightweight health endpoint for probes and uptime checks.

    Returns:
        JSON object indicating service status.
    """
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(transactions_router)
app.include_router(reports_router)
