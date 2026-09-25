"""Feedback service implementing workflow transitions and access logic."""

from __future__ import annotations

import contextlib
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationFailedError
from app.models.auth import User
from app.models.enums import FeedbackStatus
from app.models.feedback import Feedback
from app.repositories.feedback import FeedbackRepository
from app.schemas.feedback import (
    FeedbackCreateRequest,
    FeedbackItem,
    FeedbackListResponse,
    FeedbackStatusUpdateRequest,
)


class FeedbackService:
    """Manages feedback submissions and status transitions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = FeedbackRepository(session)

    async def create_feedback(
        self,
        req: FeedbackCreateRequest,
        current_user: User | None = None,
    ) -> FeedbackItem:
        """Create a new feedback item."""
        session_uuid: uuid.UUID | None = None
        if req.diagnosis_session_id:
            try:
                session_uuid = uuid.UUID(req.diagnosis_session_id)
            except ValueError:
                # If not a valid UUID, ignore or log
                session_uuid = None

        message_content = req.message
        if req.contact_info:
            message_content = f"{req.message}\n\nContact: {req.contact_info}"

        feedback = await self.repo.create(
            subject=req.subject,
            message=message_content,
            user_id=current_user.id if current_user else None,
            diagnosis_session_id=session_uuid,
        )
        loaded = await self.repo.get_by_id(feedback.id)
        return self._to_item(loaded or feedback)

    async def list_feedback(
        self,
        current_user: User | None,
        can_read_all: bool,
        status_filter: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> FeedbackListResponse:
        """List feedback items. If not can_read_all, returns only user's own feedback."""
        target_user_id = None if can_read_all else (current_user.id if current_user else -1)

        parsed_status: FeedbackStatus | None = None
        if status_filter:
            with contextlib.suppress(ValueError):
                parsed_status = FeedbackStatus(status_filter)

        items, total = await self.repo.list_paginated(
            user_id=target_user_id,
            status=parsed_status,
            page=page,
            size=size,
        )

        return FeedbackListResponse(
            items=[self._to_item(f) for f in items],
            total=total,
            page=page,
            size=size,
        )

    async def update_status(
        self,
        feedback_id: int,
        req: FeedbackStatusUpdateRequest,
    ) -> FeedbackItem:
        """Transition feedback to a new status."""
        feedback = await self.repo.get_by_id(feedback_id)
        if not feedback:
            raise NotFoundError(detail=f"Feedback #{feedback_id} not found")

        try:
            new_status = FeedbackStatus(req.status)
        except ValueError as exc:
            raise ValidationFailedError(detail=f"Invalid status: {req.status}") from exc

        updated = await self.repo.update_status(feedback, new_status)
        return self._to_item(updated)

    @staticmethod
    def _to_item(feedback: Feedback) -> FeedbackItem:
        session_id_str = (
            str(feedback.diagnosis_session_id) if feedback.diagnosis_session_id else None
        )
        return FeedbackItem(
            id=feedback.id,
            subject=feedback.subject,
            message=feedback.message,
            status=feedback.status.value,  # Convert enum to string
            created_at=feedback.created_at.isoformat(),  # Convert datetime to ISO string
            user_id=feedback.user_id,
            user_name=feedback.user.username if feedback.user else None,
            diagnosis_session_id=session_id_str,
            media_url=f"/media/{feedback.media.storage_key}" if feedback.media else None,
        )
