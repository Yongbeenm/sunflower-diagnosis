"""Application settings loaded from environment variables.

Required secrets (no default — startup fails loudly if missing):
  DATABASE_URL, JWT_SECRET, ADMIN_PASSWORD
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        # Extra env vars (e.g. POSTGRES_*) are silently ignored.
        extra="ignore",
    )

    # ---- Database ----
    DATABASE_URL: str  # no default — required
    ALEMBIC_DATABASE_URL: str = ""

    # ---- Auth (JWT_SECRET has no default — startup fails if missing) ----
    JWT_SECRET: str  # no default — required
    JWT_ALG: str = "HS256"
    ACCESS_TTL_MIN: int = 1440
    REFRESH_TTL_DAYS: int = 30

    # ---- API ----
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    # Comma-separated string. Use the cors_origins_list property in code.
    # Kept as str so pydantic-settings does not attempt JSON list parsing.
    CORS_ORIGINS: str = ""

    # ---- Media storage ----
    MEDIA_BACKEND: str = "local"
    MEDIA_ROOT: str = "/var/lib/sunflower/media"
    MEDIA_PUBLIC_URL: str = "http://localhost:8000/media"
    MEDIA_MAX_BYTES: int = 15_728_640  # 15 MB

    # ---- Seed admin (no default for password — required for seed script) ----
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str  # no default — required

    # ---- Frontend (Vite) ----
    VITE_API_BASE_URL: str = "http://localhost:8000/api/v1"

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS_ORIGINS as a list, split on commas."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENV.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings.

    Call this everywhere instead of constructing Settings() directly so that
    the environment is only parsed once.
    """
    return Settings()
