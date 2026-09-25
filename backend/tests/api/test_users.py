"""Integration tests for user self-profile updates."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from scripts.seed import seed_database


@pytest.fixture(autouse=True)
async def _seed_data(db_session: AsyncSession) -> None:
    await seed_database(db_session)


@pytest.mark.asyncio
async def test_update_me_requires_current_password(client: AsyncClient) -> None:
    """PATCH /users/me fails with 401 if current_password is wrong."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "update_test@example.com",
            "username": "update_test",
            "password": "originalPassword123!",
        },
    )
    token = reg.json()["access_token"]

    # Wrong current_password
    resp = await client.patch(
        "/api/v1/users/me",
        json={"email": "new_email@example.com", "current_password": "wrongPassword!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 401
    assert "current password" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_me_email_and_username_and_password(client: AsyncClient) -> None:
    """PATCH /users/me updates profile fields with valid current_password."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "user_me@example.com",
            "username": "user_me",
            "password": "originalPassword123!",
        },
    )
    token = reg.json()["access_token"]

    # Update email and username
    resp_update = await client.patch(
        "/api/v1/users/me",
        json={
            "email": "updated_me@example.com",
            "username": "updated_me",
            "current_password": "originalPassword123!",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_update.status_code == 200
    assert resp_update.json()["email"] == "updated_me@example.com"
    assert resp_update.json()["username"] == "updated_me"

    # Update password
    resp_pw = await client.patch(
        "/api/v1/users/me",
        json={
            "new_password": "brandNewPassword123!",
            "current_password": "originalPassword123!",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_pw.status_code == 200

    # Log in with new password
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "updated_me", "password": "brandNewPassword123!"},
    )
    assert login_resp.status_code == 200


@pytest.mark.asyncio
async def test_update_me_conflict_on_existing_email(client: AsyncClient) -> None:
    """PATCH /users/me returns 409 if chosen email is already taken."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "existing@example.com",
            "username": "existing_user",
            "password": "password123!",
        },
    )

    reg2 = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "another@example.com",
            "username": "another_user",
            "password": "password123!",
        },
    )
    token2 = reg2.json()["access_token"]

    resp = await client.patch(
        "/api/v1/users/me",
        json={"email": "existing@example.com", "current_password": "password123!"},
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert resp.status_code == 409
    assert resp.json()["type"] == "/errors/conflict"
