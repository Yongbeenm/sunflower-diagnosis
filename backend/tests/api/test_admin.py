"""API integration tests for admin console endpoints (roles, users, rulesets)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.auth import Role, User
from app.models.ruleset import Ruleset
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
async def test_roles_management(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin can view and update role-permission matrix."""
    _admin, admin_token = await _create_user_with_token(
        db_session, "super_admin", "admin", ["rbac:manage"]
    )
    _grower, grower_token = await _create_user_with_token(
        db_session, "plain_grower", "grower", ["disease:read"]
    )

    # 1. Grower cannot access /admin/roles
    resp = await client.get(
        "/api/v1/admin/roles",
        headers={"Authorization": f"Bearer {grower_token}"},
    )
    assert resp.status_code == 403

    # 2. Admin gets roles list
    resp = await client.get(
        "/api/v1/admin/roles",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "permissions" in data
    role_id = data["items"][0]["id"]

    # 3. Admin updates role permissions
    put_resp = await client.put(
        f"/api/v1/admin/roles/{role_id}/permissions",
        json={"permission_codes": ["disease:read", "symptom:read"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert put_resp.status_code == 200
    assert {
        permission["code"]
        for permission in put_resp.json()["permissions"]
        if permission["granted"]
    } == {"disease:read", "symptom:read"}


@pytest.mark.asyncio
async def test_user_management(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin can list users and update active status and roles."""
    _admin, admin_token = await _create_user_with_token(
        db_session, "user_admin", "admin", ["user:manage"]
    )
    target_user, _ = await _create_user_with_token(db_session, "target_worker", "grower", [])

    # List users
    resp = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["total"] >= 2

    # Deactivate user
    patch_resp = await client.patch(
        f"/api/v1/admin/users/{target_user.id}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_ruleset_activation(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin can list rulesets and activate a version atomically."""
    _admin, admin_token = await _create_user_with_token(
        db_session, "ruleset_admin", "admin", ["ruleset:manage"]
    )

    # Add a second inactive ruleset
    v2 = Ruleset(
        version="v2.0-experimental",
        algorithm="weighted_normalized_v2",
        params={"lambda_absent": 0.4, "min_confidence": 0.15},
        is_active=False,
    )
    db_session.add(v2)
    await db_session.commit()

    # List rulesets
    resp = await client.get(
        "/api/v1/admin/rulesets",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 2

    # Activate v2
    act_resp = await client.post(
        f"/api/v1/admin/rulesets/{v2.id}/activate",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert act_resp.status_code == 200
    assert act_resp.json()["is_active"] is True
    assert act_resp.json()["version"] == "v2.0-experimental"
