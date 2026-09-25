"""Symptom and symptom category models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.auth import User
    from app.models.disease import DiseaseSymptom


class SymptomCategory(Base):
    """Anatomy or context grouping for sunflower symptoms (e.g. leaf, stem, head)."""

    __tablename__ = "symptom_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    symptoms: Mapped[list[Symptom]] = relationship(
        "Symptom",
        back_populates="category",
        lazy="raise",
    )


class Symptom(Base, TimestampMixin):
    """Observable indicator or condition on a sunflower plant or field."""

    __tablename__ = "symptoms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("symptom_categories.id"),
        nullable=False,
    )
    is_environmental: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    category: Mapped[SymptomCategory] = relationship(
        "SymptomCategory",
        back_populates="symptoms",
        lazy="raise",
    )
    disease_symptoms: Mapped[list[DiseaseSymptom]] = relationship(
        "DiseaseSymptom",
        back_populates="symptom",
        lazy="raise",
    )
    created_by: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[created_by_id],
        lazy="raise",
    )
    updated_by: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[updated_by_id],
        lazy="raise",
    )
