"""Diagnosis session, selected symptoms, and computed result models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Uuid,
    func,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import DiagnosisAnswer, DiagnosisOutcome

if TYPE_CHECKING:
    from app.models.auth import User
    from app.models.disease import Disease
    from app.models.ruleset import Ruleset
    from app.models.symptom import Symptom


class DiagnosisSession(Base):
    """Persisted expert system diagnosis evaluation session."""

    __tablename__ = "diagnosis_sessions"
    __table_args__ = (Index("ix_diagnosis_sessions_user_created", "user_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    ruleset_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rulesets.id"),
        nullable=False,
    )
    locale: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    symptom_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    top_disease_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("diseases.id", ondelete="SET NULL"),
        nullable=True,
    )
    top_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 3),
        nullable=True,
    )
    outcome: Mapped[DiagnosisOutcome] = mapped_column(
        Enum(
            DiagnosisOutcome,
            name="diagnosis_outcome",
            native_enum=True,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped[User | None] = relationship(
        "User",
        back_populates="diagnosis_sessions",
        lazy="raise",
    )
    ruleset: Mapped[Ruleset] = relationship(
        "Ruleset",
        back_populates="diagnosis_sessions",
        lazy="raise",
    )
    top_disease: Mapped[Disease | None] = relationship(
        "Disease",
        foreign_keys=[top_disease_id],
        lazy="raise",
    )
    selected_symptoms: Mapped[list[DiagnosisSelectedSymptom]] = relationship(
        "DiagnosisSelectedSymptom",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    results: Mapped[list[DiagnosisResult]] = relationship(
        "DiagnosisResult",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="DiagnosisResult.rank",
        lazy="raise",
    )


class DiagnosisSelectedSymptom(Base):
    """User response for an individual symptom within a diagnosis session."""

    __tablename__ = "diagnosis_selected_symptoms"

    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("diagnosis_sessions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    symptom_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("symptoms.id", ondelete="CASCADE"),
        primary_key=True,
    )
    answer: Mapped[DiagnosisAnswer] = mapped_column(
        Enum(
            DiagnosisAnswer,
            name="diagnosis_answer",
            native_enum=True,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )

    session: Mapped[DiagnosisSession] = relationship(
        "DiagnosisSession",
        back_populates="selected_symptoms",
        lazy="raise",
    )
    symptom: Mapped[Symptom] = relationship(
        "Symptom",
        lazy="raise",
    )


class DiagnosisResult(Base):
    """Ranked candidate disease result and supporting evidence for a session."""

    __tablename__ = "diagnosis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("diagnosis_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    disease_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("diseases.id", ondelete="SET NULL"),
        nullable=True,
    )
    disease_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    evidence: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(postgresql.JSONB, "postgresql"),
        nullable=False,
    )

    session: Mapped[DiagnosisSession] = relationship(
        "DiagnosisSession",
        back_populates="results",
        lazy="raise",
    )
    disease: Mapped[Disease | None] = relationship(
        "Disease",
        lazy="raise",
    )
