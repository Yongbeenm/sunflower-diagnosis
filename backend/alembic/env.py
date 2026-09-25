"""Alembic async-aware environment.

Reads ALEMBIC_DATABASE_URL from the environment (sync psycopg driver).
Never reads from alembic.ini — credentials must not live in version control.

compare_type=True      — detects column type changes
compare_server_default=True — detects server-default changes
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Import Base so target_metadata includes all model tables.
# Models are imported transitively when they register against Base.
from app.db.base import Base

# ---------------------------------------------------------------------------
# Alembic Config object — gives access to values in alembic.ini
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file's logging configuration.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Database URL — read from the environment, never from alembic.ini
# ---------------------------------------------------------------------------


def _get_url() -> str:
    url = os.environ.get("ALEMBIC_DATABASE_URL", "")
    if not url:
        from app.core.config import get_settings

        url = get_settings().ALEMBIC_DATABASE_URL
    if not url:
        raise RuntimeError(
            "ALEMBIC_DATABASE_URL is not set. "
            "Copy .env.example to .env and fill in the database credentials."
        )
    return url


# ---------------------------------------------------------------------------
# Offline mode (generate SQL without a live connection)
# ---------------------------------------------------------------------------


def run_migrations_offline() -> None:
    url = _get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online mode (connect to the database)
# ---------------------------------------------------------------------------


def run_migrations_online() -> None:
    # Override the sqlalchemy.url from the environment.
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
