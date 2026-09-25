"""Authentication and user request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    """User profile data with assigned role and effective permissions."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    role: str
    permissions: list[str]
    is_active: bool


class TokenResponse(BaseModel):
    """Response returned upon successful authentication or token refresh."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterRequest(BaseModel):
    """New grower registration payload."""

    email: EmailStr
    username: str = Field(min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Credential login payload accepting username or email."""

    identifier: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UpdateMeRequest(BaseModel):
    """Payload for user self-updates.

    A username or email change requires current_password.
    A password change requires current_password.
    """

    email: EmailStr | None = None
    username: str | None = Field(
        default=None, min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$"
    )
    new_password: str | None = Field(default=None, min_length=8, max_length=128)
    current_password: str = Field(min_length=1)
