"""Authentication and user management business logic."""

from __future__ import annotations

import contextlib
from typing import Any

from app.core.errors import ConflictError, ForbiddenError, UnauthorizedError
from app.core.rate_limit import login_rate_limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_legacy_hash,
    token_store,
    verify_dummy_password,
    verify_password,
)
from app.models.auth import User
from app.repositories.user import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UpdateMeRequest,
    UserResponse,
)


def user_to_response(user: User) -> UserResponse:
    """Convert User ORM model to UserResponse schema with flattened permissions."""
    permission_codes = sorted([p.code for p in user.role.permissions]) if user.role else []
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role.name if user.role else "unknown",
        permissions=permission_codes,
        is_active=user.is_active,
    )


class AuthService:
    """Authentication and profile management service."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register(self, req: RegisterRequest) -> tuple[TokenResponse, str]:
        """Register a new grower account.

        Raises:
            ConflictError: if email or username is already taken.
        """
        existing_email = await self.user_repo.get_by_email(req.email)
        if existing_email:
            raise ConflictError(detail="A user with this email already exists")

        existing_username = await self.user_repo.get_by_username(req.username)
        if existing_username:
            raise ConflictError(detail="A user with this username already exists")

        grower_role = await self.user_repo.get_role_by_name("grower")
        if not grower_role:
            raise RuntimeError("Default 'grower' role is not seeded in database")

        user = User(
            email=req.email,
            username=req.username,
            password_hash=hash_password(req.password),
            role_id=grower_role.id,
            is_active=True,
        )
        created_user = await self.user_repo.create(user)

        user_resp = user_to_response(created_user)
        access_token, _ = create_access_token(
            created_user.id,
            user_resp.role,
            user_resp.permissions,
        )
        refresh_token, _ = create_refresh_token(created_user.id)

        token_resp = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_resp,
        )
        return token_resp, refresh_token

    async def login(self, req: LoginRequest, client_ip: str) -> tuple[TokenResponse, str]:
        """Authenticate user with rate limiting and constant-time failure timing.

        Returns:
            (TokenResponse, refresh_token_string)
        """
        # Rate limit: 10 attempts per 15 minutes per (ip, identifier)
        rate_key = f"{client_ip}:{req.identifier.lower()}"
        login_rate_limiter.check_and_record(rate_key, max_attempts=10, window_seconds=900)

        user = await self.user_repo.get_by_identifier(req.identifier)
        if not user:
            verify_dummy_password(req.password)
            raise UnauthorizedError(detail="Invalid email/username or password")

        if not verify_password(req.password, user.password_hash):
            raise UnauthorizedError(detail="Invalid email/username or password")

        # Transparently upgrade legacy Werkzeug hashes to Argon2id upon successful authentication
        if is_legacy_hash(user.password_hash):
            user.password_hash = hash_password(req.password)
            await self.user_repo.session.flush()

        if not user.is_active:
            raise ForbiddenError(detail="User account is inactive")

        user_resp = user_to_response(user)
        access_token, _ = create_access_token(
            user.id,
            user_resp.role,
            user_resp.permissions,
        )
        refresh_token, _ = create_refresh_token(user.id)

        token_resp = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_resp,
        )
        return token_resp, refresh_token

    async def refresh_tokens(self, old_refresh_token: str) -> tuple[TokenResponse, str]:
        """Validate and rotate refresh token.

        Revokes the old jti and returns a new access token and rotated refresh token.
        """
        payload = decode_token(old_refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError(detail="Invalid token type")

        jti = payload.get("jti")
        if not jti or not token_store.is_valid(jti):
            raise UnauthorizedError(detail="Refresh token has been revoked or is invalid")

        # Invalidate the old token immediately
        token_store.revoke(jti)

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise UnauthorizedError(detail="Invalid token payload")

        user = await self.user_repo.get_by_id(int(user_id_str))
        if not user or not user.is_active:
            raise UnauthorizedError(detail="User no longer active or exists")

        user_resp = user_to_response(user)
        new_access, _ = create_access_token(user.id, user_resp.role, user_resp.permissions)
        new_refresh, _ = create_refresh_token(user.id)

        token_resp = TokenResponse(
            access_token=new_access,
            token_type="bearer",
            user=user_resp,
        )
        return token_resp, new_refresh

    def logout(self, refresh_token: str | None) -> None:
        """Revoke refresh token if valid."""
        if not refresh_token:
            return
        with contextlib.suppress(Exception):
            payload: dict[str, Any] = decode_token(refresh_token)
            jti = payload.get("jti")
            if jti:
                token_store.revoke(jti)

    async def update_me(self, user: User, req: UpdateMeRequest) -> UserResponse:
        """Update current user profile. Requires current_password verification."""
        if not verify_password(req.current_password, user.password_hash):
            raise UnauthorizedError(detail="Current password is required and incorrect")

        if req.email is not None and req.email != user.email:
            existing_email = await self.user_repo.get_by_email(req.email)
            if existing_email:
                raise ConflictError(detail="A user with this email already exists")
            user.email = req.email

        if req.username is not None and req.username != user.username:
            existing_username = await self.user_repo.get_by_username(req.username)
            if existing_username:
                raise ConflictError(detail="A user with this username already exists")
            user.username = req.username

        if req.new_password is not None:
            user.password_hash = hash_password(req.new_password)

        await self.user_repo.session.flush()
        # Re-fetch with loaded relationships
        updated = await self.user_repo.get_by_id(user.id)
        assert updated is not None
        return user_to_response(updated)
