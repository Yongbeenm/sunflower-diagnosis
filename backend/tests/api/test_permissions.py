"""Tests for require_permission and fail-closed security enforcement."""

from __future__ import annotations

import pytest
from fastapi import APIRouter, Depends
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_permission
from app.core.security import create_access_token
from app.main import create_app
from app.models.auth import Role, User
from scripts.seed import seed_database


@pytest.fixture(autouse=True)
async def _seed_data(db_session: AsyncSession) -> None:
    await seed_database(db_session)


@pytest.mark.asyncio
async def test_permission_granted_and_denied(db_session: AsyncSession) -> None:
    """User with required permission is allowed; user lacking permission gets 403."""
    app = create_app()

    test_router = APIRouter()

    @test_router.get(
        "/protected/disease-create", dependencies=[Depends(require_permission("disease:create"))]
    )
    async def _protected_disease_create() -> dict[str, str]:
        return {"status": "success"}

    app.include_router(test_router)

    # Override get_db for testing
    async def _override_get_db() -> AsyncSession:
        return db_session

    app.dependency_overrides[get_db] = _override_get_db

    # Create a dedicated grower user
    result = await db_session.execute(select(Role).where(Role.name == "grower"))
    grower_role = result.scalar_one()

    grower_user = User(
        email="grower_test@example.com",
        username="grower_test",
        password_hash="fakehash",
        role_id=grower_role.id,
        is_active=True,
    )
    db_session.add(grower_user)
    await db_session.flush()

    # Load the seeded admin user
    admin_result = await db_session.execute(select(User).where(User.username == "admin"))
    admin_user = admin_result.scalar_one()

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Grower token lacks 'disease:create' -> 403
        grower_token, _ = create_access_token(
            user_id=grower_user.id, role="grower", permissions=["disease:read"]
        )
        resp_denied = await ac.get(
            "/protected/disease-create",
            headers={"Authorization": f"Bearer {grower_token}"},
        )
        assert resp_denied.status_code == 403
        assert resp_denied.json()["type"] == "/errors/forbidden"

        # 2. Admin has 'disease:create' -> 200
        admin_token, _ = create_access_token(
            user_id=admin_user.id, role="admin", permissions=["disease:create"]
        )
        resp_granted = await ac.get(
            "/protected/disease-create",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp_granted.status_code == 200
        assert resp_granted.json() == {"status": "success"}


@pytest.mark.asyncio
async def test_permission_fails_closed_on_error(
    db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When a database or system error occurs during permission evaluation,
    access MUST fail closed (403).
    """
    app = create_app()

    test_router = APIRouter()

    @test_router.get(
        "/protected/fail-closed", dependencies=[Depends(require_permission("user:manage"))]
    )
    async def _protected_fail_closed() -> dict[str, str]:
        return {"status": "should_never_reach_here"}

    app.include_router(test_router)

    async def _override_get_db() -> AsyncSession:
        return db_session

    app.dependency_overrides[get_db] = _override_get_db

    # Simulate an OperationalError during permission evaluation (e.g. legacy app had
    # except OperationalError: return self.role == "admin" — our system MUST fail closed)
    def _faulty_has_permission(self: User, code: str) -> bool:
        raise OperationalError(
            "SELECT * FROM role_permissions ...", {}, Exception("Simulated DB failure")
        )

    monkeypatch.setattr(User, "has_permission", _faulty_has_permission)

    admin_result = await db_session.execute(select(User).where(User.username == "admin"))
    admin_user = admin_result.scalar_one()
    admin_token, _ = create_access_token(
        user_id=admin_user.id, role="admin", permissions=["user:manage"]
    )

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/protected/fail-closed",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        # CRITICAL: MUST be 403 Forbidden, NEVER 200 or 500 granting access
        assert response.status_code == 403
        assert response.json()["type"] == "/errors/forbidden"
