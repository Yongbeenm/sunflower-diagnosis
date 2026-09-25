"""FastAPI dependency providers for database access, authentication, and RBAC."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
from typing import Annotated, Any

import structlog
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.db.session import async_session_factory
from app.models.auth import User
from app.repositories.user import UserRepository

log = structlog.get_logger(__name__)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async SQLAlchemy session with rollback on uncaught exceptions."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    """Extract and validate bearer access token and load the active user.

    Raises:
        UnauthorizedError (401): if token is missing, invalid, or expired.
        ForbiddenError (403): if the authenticated user account is inactive.
    """
    if not authorization:
        raise UnauthorizedError(detail="Missing authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError(detail="Invalid authorization header scheme")

    token = parts[1]
    payload = decode_token(token)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError(detail="Invalid token subject")

    try:
        user_id = int(user_id_str)
    except ValueError as exc:
        raise UnauthorizedError(detail="Malformed user ID in token") from exc

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UnauthorizedError(detail="User no longer exists")

    if not user.is_active:
        raise ForbiddenError(detail="User account is inactive")

    return user


async def get_optional_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorization: Annotated[str | None, Header()] = None,
) -> User | None:
    """Extract user if valid bearer token is provided; returns None otherwise."""
    if not authorization:
        return None
    try:
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        payload = decode_token(parts[1])
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        user_id = int(user_id_str)
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None


def require_permission(code: str) -> Callable[..., Any]:
    """Dependency factory that enforces a specific permission code on the endpoint.

    MUST fail closed: any unexpected exception during checking raises ForbiddenError (403).
    """

    async def _permission_dependency(
        user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        try:
            # Check user's role permissions
            if not user.has_permission(code):
                log.info(
                    "rbac.permission_denied",
                    user_id=user.id,
                    role=user.role.name if user.role else None,
                    required=code,
                )
                raise ForbiddenError(detail=f"Permission denied: required '{code}'")

            return user
        except ForbiddenError:
            raise
        except Exception as exc:
            # Explicit fail-closed policy: never grant access on failure
            log.error("rbac.check_failed_fail_closed", error=str(exc), user_id=user.id, code=code)
            raise ForbiddenError(detail="Access evaluation failed") from exc

    return _permission_dependency
