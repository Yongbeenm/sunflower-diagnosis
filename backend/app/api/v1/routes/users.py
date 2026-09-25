"""User management routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.auth import User
from app.repositories.user import UserRepository
from app.schemas.auth import UpdateMeRequest, UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/users", tags=["users"])


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile (requires current_password)",
)
async def update_me(
    req: UpdateMeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Update username, email, or password for the authenticated user.

    A username or email change requires current_password.
    A password change requires current_password.
    """
    service = AuthService(UserRepository(db))
    return await service.update_me(current_user, req)
