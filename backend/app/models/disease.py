"""Disease and DiseaseSymptom knowledge base association models."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PathogenType
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.auth import User
    from app.models.media import Media
    from app.models.symptom import Symptom


class Disease(Base, TimestampMixin):
    """Botanical sunflower disease or abiotic disorder candidate."""

    __tablename__ = "diseases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    pathogen_type: Mapped[PathogenType] = mapped_column(
        Enum(
            PathogenType,
            name="pathogen_type",
            native_enum=True,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    image_media_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("media.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    search_vector: Mapped[Any | None] = mapped_column(
        Text().with_variant(postgresql.TSVECTOR, "postgresql"),
        nullable=True,
    )
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

    disease_symptoms: Mapped[list[DiseaseSymptom]] = relationship(
        "DiseaseSymptom",
        back_populates="disease",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    image_media: Mapped[Media | None] = relationship(
        "Media",
        foreign_keys=[image_media_id],
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


class DiseaseSymptom(Base):
    """Knowledge base rule linking a disease with a weighted symptom."""

    __tablename__ = "disease_symptoms"
    __table_args__ = (
        CheckConstraint(
            "weight >= 0 AND weight <= 1",
            name="ck_disease_symptoms_weight_range",
        ),
    )

    disease_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("diseases.id", ondelete="CASCADE"),
        primary_key=True,
    )
    symptom_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("symptoms.id", ondelete="CASCADE"),
        primary_key=True,
    )
    weight: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_pathognomonic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    disease: Mapped[Disease] = relationship(
        "Disease",
        back_populates="disease_symptoms",
        lazy="raise",
    )
    symptom: Mapped[Symptom] = relationship(
        "Symptom",
        back_populates="disease_symptoms",
        lazy="raise",
    )
