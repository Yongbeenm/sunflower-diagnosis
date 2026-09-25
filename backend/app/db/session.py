"""Async SQLAlchemy engine, session factory, and FastAPI dependency.

Design decisions:
- expire_on_commit=False so that returned ORM objects remain accessible after
  the session commits (avoids lazy-load errors in serialisers).
- get_db() rolls back on any exception so a failed request never leaves a
  half-committed transaction open.
- The engine is created once at import time from the cached settings; tests
  override it via dependency injection.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

log = structlog.get_logger(__name__)

_settings = get_settings()

# Configure engine with connection arguments for Supabase pooling compatibility
connect_args = {}
if "pooler.supabase.com" in _settings.DATABASE_URL:
    # Disable prepared statements for Supabase transaction pooling
    connect_args["statement_cache_size"] = 0

engine: AsyncEngine = create_async_engine(
    _settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=not _settings.is_production,
    connect_args=connect_args,
)

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a transactional AsyncSession.

    Rolls back on any exception; always closes in the finally block.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
