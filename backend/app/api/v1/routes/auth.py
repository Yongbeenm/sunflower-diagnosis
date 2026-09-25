"""Authentication API routes: register, login, refresh, logout, me."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import get_current_user, get_db
from app.core.errors import UnauthorizedError
from app.models.auth import User
from app.repositories.user import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth import AuthService, user_to_response

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/"


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    settings = get_settings()
    # 30 days TTL in seconds
    max_age = settings.REFRESH_TTL_DAYS * 24 * 60 * 60
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        path=REFRESH_COOKIE_PATH,
        max_age=max_age,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path=REFRESH_COOKIE_PATH,
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new grower",
)
async def register(
    req: RegisterRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Register a new grower account and issue initial access/refresh tokens."""
    service = AuthService(UserRepository(db))
    token_resp, refresh_token = await service.register(req)
    _set_refresh_cookie(response, refresh_token)
    return token_resp


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate with username or email and password",
)
async def login(
    req: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Authenticate credentials, issue access token, and set refresh cookie."""
    client_ip = request.client.host if request.client else "unknown"
    service = AuthService(UserRepository(db))
    token_resp, refresh_token = await service.login(req, client_ip)
    _set_refresh_cookie(response, refresh_token)
    return token_resp


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate refresh token and issue new access token",
)
async def refresh(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE_NAME)] = None,
) -> TokenResponse:
    """Rotate the refresh token and return a fresh access token."""
    if not refresh_token:
        raise UnauthorizedError(detail="Missing refresh token cookie")

    service = AuthService(UserRepository(db))
    token_resp, new_refresh = await service.refresh_tokens(refresh_token)
    _set_refresh_cookie(response, new_refresh)
    return token_resp


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out and invalidate refresh token",
)
async def logout(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE_NAME)] = None,
) -> None:
    """Clear the refresh token cookie and invalidate its server-side jti."""
    service = AuthService(UserRepository(db))
    service.logout(refresh_token)
    _clear_refresh_cookie(response)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile and permissions",
)
async def me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Return the profile, role, and permission capabilities of the active user."""
    return user_to_response(current_user)
