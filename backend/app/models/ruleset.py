"""Ruleset model governing diagnosis scoring algorithm and parameters."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.auth import User
    from app.models.diagnosis import DiagnosisSession


class Ruleset(Base):
    """Versioned diagnosis engine configuration and hyperparameters."""

    __tablename__ = "rulesets"
    __table_args__ = (
        Index(
            "uq_rulesets_single_active",
            "is_active",
            unique=True,
            postgresql_where=text("is_active = true"),
            sqlite_where=text("is_active = 1"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    algorithm: Mapped[str] = mapped_column(String(64), nullable=False)
    params: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(postgresql.JSONB, "postgresql"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    published_by_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    published_by: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[published_by_id],
        lazy="raise",
    )
    diagnosis_sessions: Mapped[list[DiagnosisSession]] = relationship(
        "DiagnosisSession",
        back_populates="ruleset",
        lazy="raise",
    )
