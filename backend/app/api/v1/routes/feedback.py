"""Feedback API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_optional_current_user, require_permission
from app.core.errors import UnauthorizedError
from app.models.auth import User
from app.schemas.feedback import (
    FeedbackCreateRequest,
    FeedbackItem,
    FeedbackListResponse,
    FeedbackStatusUpdateRequest,
)
from app.services.feedback import FeedbackService

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.get(
    "",
    response_model=FeedbackListResponse,
    summary="List feedback reports (all for agronomist/admin, own for grower)",
)
async def list_feedback(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
    status: Annotated[str | None, Query(description="Filter by feedback status")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> FeedbackListResponse:
    """List feedback. Users with feedback:read see all; regular growers see own."""
    if not current_user:
        raise UnauthorizedError(detail="Authentication required to view feedback")

    can_read_all = current_user.has_permission("feedback:read")
    
    # Debug logging
    print("\n[FEEDBACK API] ===== LIST FEEDBACK =====")
    print(f"[FEEDBACK API] User: {current_user.email}")
    print(f"[FEEDBACK API] User ID: {current_user.id}")
    print(f"[FEEDBACK API] Role: {current_user.role.name if current_user.role else 'None'}")
    print(f"[FEEDBACK API] Has feedback:read permission: {can_read_all}")
    print(f"[FEEDBACK API] Status filter: {status}")
    print(f"[FEEDBACK API] Page: {page}, Size: {size}")
    
    service = FeedbackService(db)
    result = await service.list_feedback(
        current_user=current_user,
        can_read_all=can_read_all,
        status_filter=status,
        page=page,
        size=size,
    )
    
    print(f"[FEEDBACK API] Total feedback found: {result.total}")
    print(f"[FEEDBACK API] Items in this page: {len(result.items)}")
    
    return result


@router.post(
    "",
    response_model=FeedbackItem,
    status_code=status.HTTP_201_CREATED,
    summary="Submit user feedback or report an unidentified issue",
)
async def create_feedback(
    req: FeedbackCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
) -> FeedbackItem:
    """Create a feedback entry."""
    service = FeedbackService(db)
    return await service.create_feedback(req=req, current_user=current_user)


@router.patch(
    "/{feedback_id}",
    response_model=FeedbackItem,
    summary="Update feedback workflow status",
    dependencies=[Depends(require_permission("feedback:resolve"))],
)
async def update_feedback_status(
    feedback_id: int,
    req: FeedbackStatusUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FeedbackItem:
    """Transition feedback status (open, in_progress, resolved, dismissed)."""
    service = FeedbackService(db)
    return await service.update_status(feedback_id=feedback_id, req=req)
