"""Grower and agronomist feedback models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import FeedbackStatus

if TYPE_CHECKING:
    from app.models.auth import User
    from app.models.diagnosis import DiagnosisSession
    from app.models.media import Media


class Feedback(Base):
    """User feedback on diagnosis outcomes or general system feedback."""

    __tablename__ = "feedback"
    __table_args__ = (Index("ix_feedback_status_created", "status", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    diagnosis_session_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("diagnosis_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    media_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("media.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[FeedbackStatus] = mapped_column(
        Enum(
            FeedbackStatus,
            name="feedback_status",
            native_enum=True,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=FeedbackStatus.OPEN,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped[User | None] = relationship(
        "User",
        back_populates="feedback",
        lazy="raise",
    )
    diagnosis_session: Mapped[DiagnosisSession | None] = relationship(
        "DiagnosisSession",
        lazy="raise",
    )
    media: Mapped[Media | None] = relationship(
        "Media",
        lazy="raise",
    )
