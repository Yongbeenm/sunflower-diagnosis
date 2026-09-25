"""Repository for feedback queries and status management."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import FeedbackStatus
from app.models.feedback import Feedback


class FeedbackRepository:
    """Repository handling feedback persistence and retrieval."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        subject: str,
        message: str,
        user_id: int | None = None,
        diagnosis_session_id: uuid.UUID | None = None,
        media_id: int | None = None,
    ) -> Feedback:
        """Create new feedback record."""
        feedback = Feedback(
            subject=subject,
            message=message,
            user_id=user_id,
            diagnosis_session_id=diagnosis_session_id,
            media_id=media_id,
            status=FeedbackStatus.OPEN,
        )
        self.session.add(feedback)
        await self.session.flush()
        return feedback

    async def get_by_id(self, feedback_id: int) -> Feedback | None:
        """Fetch single feedback by ID with relations loaded."""
        stmt = (
            select(Feedback)
            .where(Feedback.id == feedback_id)
            .options(
                selectinload(Feedback.user),
                selectinload(Feedback.media),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_paginated(
        self,
        user_id: int | None = None,
        status: FeedbackStatus | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Feedback], int]:
        """List feedback items with optional user and status filters."""
        # Debug logging
        print("\n[FEEDBACK REPO] ===== LIST PAGINATED =====")
        print(f"[FEEDBACK REPO] user_id filter: {user_id}")
        print(f"[FEEDBACK REPO] status filter: {status}")
        print(f"[FEEDBACK REPO] page: {page}, size: {size}")
        
        base_query = select(Feedback)
        count_query = select(func.count(Feedback.id))

        if user_id is not None:
            print(f"[FEEDBACK REPO] Filtering by user_id = {user_id}")
            base_query = base_query.where(Feedback.user_id == user_id)
            count_query = count_query.where(Feedback.user_id == user_id)

        if status is not None:
            print(f"[FEEDBACK REPO] Filtering by status = {status}")
            base_query = base_query.where(Feedback.status == status)
            count_query = count_query.where(Feedback.status == status)

        total = await self.session.scalar(count_query) or 0
        print(f"[FEEDBACK REPO] Total count: {total}")

        stmt = (
            base_query.options(
                selectinload(Feedback.user),
                selectinload(Feedback.media),
            )
            .order_by(Feedback.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        res = await self.session.execute(stmt)
        items = list(res.scalars().all())
        
        print(f"[FEEDBACK REPO] Items fetched: {len(items)}")
        for item in items:
            print(f"[FEEDBACK REPO]   - ID: {item.id}, Subject: {item.subject}, User ID: {item.user_id}, Status: {item.status}")

        return items, total

    async def update_status(self, feedback: Feedback, status: FeedbackStatus) -> Feedback:
        """Update feedback workflow status."""
        feedback.status = status
        await self.session.flush()
        return feedback
