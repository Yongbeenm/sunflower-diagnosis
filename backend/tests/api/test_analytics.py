"""API tests for analytics overview endpoint."""

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
async def test_analytics_requires_auth(client: AsyncClient) -> None:
    """GET /analytics/overview returns 401 without bearer token."""
    resp = await client.get("/api/v1/analytics/overview")
    assert resp.status_code == 401
    assert resp.headers["content-type"] == "application/problem+json"


@pytest.mark.asyncio
async def test_analytics_forbidden_for_grower(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /analytics/overview returns 403 for grower without analytics:read."""
    _user, token = await _create_user_with_token(
        db_session, "grower_user", "grower", ["diagnosis:run"]
    )
    resp = await client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_analytics_success_for_agronomist(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /analytics/overview returns 200 with metrics for agronomist."""
    _user, token = await _create_user_with_token(
        db_session, "agro_analytics", "agronomist", ["analytics:read"]
    )
    resp = await client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "checks_today" in data
    assert "checks_total" in data
    assert "checks_trend_30d" in data
    assert "top_symptoms" in data
    assert "no_match_patterns" in data
    assert "pending_feedback_count" in data
