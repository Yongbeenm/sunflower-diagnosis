"""FastAPI application factory.

Call create_app() to get a configured FastAPI instance. The module-level
`app` symbol is what uvicorn imports.

Startup order:
  1. Load settings (fails loudly if required secrets are missing).
  2. Configure structlog.
  3. Build FastAPI with CORS, exception handlers, and request-id middleware.
  4. Mount the /api/v1 router (empty in Step 1; routes added in later steps).
  5. Register GET /health.
"""

from __future__ import annotations

import structlog
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import get_settings
from app.core.errors import AppError, app_error_handler, validation_error_handler
from app.core.logging import RequestIdMiddleware, configure_logging
from app.db.session import async_session_factory

log = structlog.get_logger(__name__)

APP_VERSION = "0.1.0"


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    application = FastAPI(
        title="Sunflower Diagnosis API",
        version=APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # --- CORS ---
    cors_origins = settings.cors_origins_list or [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Request-id middleware ---
    application.add_middleware(RequestIdMiddleware)

    # --- Exception handlers ---
    application.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    application.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]

    # --- Root endpoint ---
    @application.get("/", tags=["ops"], include_in_schema=False)
    async def root() -> dict[str, str]:
        """Root API information."""
        return {
            "name": "Sunflower Diagnosis API",
            "version": APP_VERSION,
            "docs": "/docs",
            "health": "/health",
            "api_v1": "/api/v1",
        }

    # --- Health endpoint ---
    @application.get("/health", tags=["ops"])
    async def health() -> dict[str, str]:
        """Liveness + readiness probe.

        Always returns HTTP 200. Callers must check the `db` field:
          "up"   — SELECT 1 succeeded
          "down" — database is unreachable
        """
        db_status = "down"
        try:
            async with async_session_factory() as session:
                await session.execute(text("SELECT 1"))
            db_status = "up"
        except Exception:
            log.warning("health.db_ping_failed")

        return {"status": "ok", "version": APP_VERSION, "db": db_status}

    # --- Static media files (when local backend) ---
    from pathlib import Path

    from fastapi.staticfiles import StaticFiles

    try:
        media_path = Path(settings.MEDIA_ROOT)
        media_path.mkdir(parents=True, exist_ok=True)
        application.mount(
            "/media",
            StaticFiles(directory=settings.MEDIA_ROOT, check_dir=False),
            name="media",
        )
    except (PermissionError, OSError) as exc:
        log.warning("media.mount_skipped", path=settings.MEDIA_ROOT, error=str(exc))

    # --- API v1 router ---
    from app.api.v1 import router as api_v1_router

    application.include_router(api_v1_router, prefix="/api/v1")

    return application


app = create_app()
