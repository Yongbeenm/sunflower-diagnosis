"""SQLAlchemy DeclarativeBase with a stable constraint-naming convention.

All constraint names are derived from their table and column names so that
Alembic autogenerate produces deterministic, collision-free names across
databases. This eliminates the "unnamed constraint" drift that plagued the
legacy schema.

Naming patterns:
  ix_<table>_<col>           — index
  uq_<table>_<col>           — unique constraint
  ck_<table>_<constraint>    — check constraint
  fk_<table>_<col>_<ref>     — foreign key
  pk_<table>                 — primary key
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Project-wide declarative base.

    Import this in every model module. Never call create_all() — use
    Alembic migrations exclusively.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
