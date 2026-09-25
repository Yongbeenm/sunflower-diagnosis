"""API integration tests for feedback workflow."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.auth import Role, User
from scripts.seed import seed_database


@pytest.fixture(autouse=True)
async def _seed_data(db_session: AsyncSession) -> None:
    await seed_database(db_session)


async def _create_user_with_token(
    db_session: AsyncSession,
    username: str,
    role_name: str,
    permissions: list[str],
) -> tuple[User, str]:
    role_res = await db_session.execute(select(Role).where(Role.name == role_name))
    role = role_res.scalar_one()

    user = User(
        email=f"{username}@example.com",
        username=username,
        password_hash="fakehash",
        role_id=role.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    token, _ = create_access_token(
        user_id=user.id,
        role=role_name,
        permissions=permissions,
    )
    return user, token


@pytest.mark.asyncio
async def test_create_and_list_feedback(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Grower can submit feedback and list their own; agronomist sees all."""
    _grower, grower_token = await _create_user_with_token(
        db_session, "grower_fb", "grower", ["feedback:create"]
    )
    _agro, agro_token = await _create_user_with_token(
        db_session, "agro_fb", "agronomist", ["feedback:read", "feedback:resolve"]
    )

    # 1. Grower posts feedback
    create_resp = await client.post(
        "/api/v1/feedback",
        json={"subject": "Stem borer issue", "message": "Observed holes on sunflower stalks"},
        headers={"Authorization": f"Bearer {grower_token}"},
    )
    assert create_resp.status_code == 201
    fb_data = create_resp.json()
    assert fb_data["subject"] == "Stem borer issue"
    assert fb_data["status"] == "open"
    fb_id = fb_data["id"]

    # 2. Grower lists feedback -> sees 1 item
    list_grower = await client.get(
        "/api/v1/feedback",
        headers={"Authorization": f"Bearer {grower_token}"},
    )
    assert list_grower.status_code == 200
    assert list_grower.json()["total"] == 1

    # 3. Agronomist lists feedback -> sees the item
    list_agro = await client.get(
        "/api/v1/feedback",
        headers={"Authorization": f"Bearer {agro_token}"},
    )
    assert list_agro.status_code == 200
    assert list_agro.json()["total"] >= 1

    # 4. Grower tries to resolve -> 403 Forbidden
    patch_grower = await client.patch(
        f"/api/v1/feedback/{fb_id}",
        json={"status": "resolved"},
        headers={"Authorization": f"Bearer {grower_token}"},
    )
    assert patch_grower.status_code == 403

    # 5. Agronomist resolves -> 200 OK
    patch_agro = await client.patch(
        f"/api/v1/feedback/{fb_id}",
        json={"status": "resolved"},
        headers={"Authorization": f"Bearer {agro_token}"},
    )
    assert patch_agro.status_code == 200
    assert patch_agro.json()["status"] == "resolved"
