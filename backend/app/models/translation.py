"""Unified multilingual translations table."""

from __future__ import annotations

from sqlalchemy import Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Translation(Base):
    """Normalized content translation for diseases, symptoms, and categories.

    Per-field fallback to English when a requested translation is missing.
    """

    __tablename__ = "translations"
    __table_args__ = (Index("ix_translations_lookup", "entity_type", "entity_id", "locale"),)

    entity_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    entity_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    locale: Mapped[str] = mapped_column(String(10), primary_key=True)
    field: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
