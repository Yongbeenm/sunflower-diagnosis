"""Pytest fixtures for the Sunflower API test suite.

Three fixtures are provided:

  app_instance — the FastAPI application with settings overridden for tests.
  client       — httpx.AsyncClient using ASGITransport (no live HTTP port).
  db_session   — an AsyncSession that wraps every test in a SAVEPOINT so the
                 test is rolled back after it completes, keeping the database
                 clean without tearing down the schema.

Database strategy
-----------------
Tests run against an in-memory SQLite database (via aiosqlite) so that:
  - No external Postgres is required in CI.
  - Each test suite is fully isolated.
  - Schema is created via Base.metadata.create_all() — acceptable here
    because tests run *against* the current model state, not migrations.

Event loop strategy
-------------------
All async fixtures use function scope (pytest-asyncio default). The
StaticPool ensures every connection goes through the same underlying
sqlite3.Connection, and we create schema per-test-function. This avoids
the session-scope / function-scope event loop mismatch that causes
'no such table' errors in pytest-asyncio >= 1.0.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Set required secrets before any app module imports Settings.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret-not-for-production")
os.environ.setdefault("ADMIN_PASSWORD", "test-admin-password")
os.environ.setdefault("ALEMBIC_DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("MEDIA_ROOT", "/tmp/sunflower_test_media")

from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  — force model registration on Base.metadata
from app.core.deps import get_db
from app.db.base import Base
from app.main import create_app

# ---------------------------------------------------------------------------
# In-memory SQLite engine shared across the test session.
# StaticPool guarantees a single underlying connection object, so create_all
# and subsequent queries all see the same database state.
# ---------------------------------------------------------------------------

_test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

_test_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=_test_engine,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(autouse=True)
async def _create_schema() -> AsyncGenerator[None, None]:
    """Create all tables before each test; drop them at teardown.

    Using function scope (the default) avoids event loop mismatch with
    pytest-asyncio >= 1.0 where session-scoped async fixtures run on a
    separate loop from function-scoped test coroutines.

    This is cheap for in-memory SQLite (typically < 5 ms).
    """
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a session bound to the test engine.

    No SAVEPOINT nesting — instead we drop all tables in _create_schema
    teardown, giving each test a pristine database.
    """
    async with _test_session_factory() as session:
        yield session


@pytest.fixture()
def app_instance(db_session: AsyncSession) -> FastAPI:
    """FastAPI app with get_db overridden to use the test session.

    IMPORTANT: we override app.core.deps.get_db (not app.db.session.get_db)
    because all route modules import get_db from app.core.deps.
    """
    application = create_app()

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    application.dependency_overrides[get_db] = _override_get_db
    return application


@pytest_asyncio.fixture()
async def client(app_instance: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client wired to the test app via ASGITransport."""
    transport = ASGITransport(app=app_instance)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
