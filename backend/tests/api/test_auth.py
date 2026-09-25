"""Integration tests for authentication flows."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import login_rate_limiter
from scripts.seed import seed_database


@pytest.fixture(autouse=True)
async def _seed_data(db_session: AsyncSession) -> None:
    """Ensure database has roles and permissions seeded."""
    await seed_database(db_session)
    login_rate_limiter.reset()


@pytest.mark.asyncio
async def test_register_creates_grower(client: AsyncClient) -> None:
    """POST /auth/register creates a grower account and returns tokens."""
    payload = {
        "email": "grower1@example.com",
        "username": "grower_one",
        "password": "strongPassword123!",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "grower1@example.com"
    assert body["user"]["role"] == "grower"
    assert "disease:read" in body["user"]["permissions"]
    assert "set-cookie" in response.headers
    assert "refresh_token" in response.headers["set-cookie"]


@pytest.mark.asyncio
async def test_register_duplicate_conflict(client: AsyncClient) -> None:
    """Duplicate email or username returns 409 Conflict with problem+json."""
    payload = {
        "email": "duplicate@example.com",
        "username": "unique_user_1",
        "password": "strongPassword123!",
    }
    resp1 = await client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201

    # Duplicate email
    resp2 = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "username": "unique_user_2",
            "password": "password123!",
        },
    )
    assert resp2.status_code == 409
    assert resp2.headers["content-type"].startswith("application/problem+json")
    assert resp2.json()["type"] == "/errors/conflict"

    # Duplicate username
    resp3 = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "different@example.com",
            "username": "unique_user_1",
            "password": "password123!",
        },
    )
    assert resp3.status_code == 409


@pytest.mark.asyncio
async def test_login_success_and_timing_uniformity(client: AsyncClient) -> None:
    """POST /auth/login verifies credentials and handles non-existent users identically."""
    # Register a user
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login_user@example.com",
            "username": "login_user",
            "password": "realPassword123!",
        },
    )

    # Valid login with email
    resp = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "login_user@example.com", "password": "realPassword123!"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert "set-cookie" in resp.headers

    # Valid login with username
    resp_user = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "login_user", "password": "realPassword123!"},
    )
    assert resp_user.status_code == 200

    # Wrong password
    resp_wrong_pw = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "login_user", "password": "wrongPassword123!"},
    )
    assert resp_wrong_pw.status_code == 401

    # Unknown account
    resp_unknown = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "unknown_user@example.com", "password": "wrongPassword123!"},
    )
    assert resp_unknown.status_code == 401

    # Identical error detail ensures no user enumeration
    assert resp_wrong_pw.json()["detail"] == resp_unknown.json()["detail"]


@pytest.mark.asyncio
async def test_login_rate_limiting(client: AsyncClient) -> None:
    """Rate limits after 10 attempts within 15 minutes."""
    login_rate_limiter.reset()

    for _ in range(10):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"identifier": "ratelimit_test", "password": "badPassword123!"},
        )
        assert resp.status_code == 401

    # 11th attempt must be rate-limited
    resp_blocked = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "ratelimit_test", "password": "badPassword123!"},
    )
    assert resp_blocked.status_code == 429
    assert resp_blocked.json()["type"] == "/errors/rate-limit-exceeded"


@pytest.mark.asyncio
async def test_refresh_token_rotation(client: AsyncClient) -> None:
    """POST /auth/refresh rotates the refresh token and rejects old tokens."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresh_test@example.com",
            "username": "refresh_test",
            "password": "password123!",
        },
    )
    cookie_header = reg.headers.get("set-cookie", "")
    assert "refresh_token=" in cookie_header
    cookie_val = cookie_header.split("refresh_token=")[1].split(";")[0]

    # First refresh: succeeds
    client.cookies.set("refresh_token", cookie_val)
    resp_refresh = await client.post("/api/v1/auth/refresh")
    assert resp_refresh.status_code == 200
    new_token = resp_refresh.json()["access_token"]
    assert new_token

    # Reusing the old cookie: MUST fail because old jti is invalidated
    client.cookies.set("refresh_token", cookie_val)
    resp_replay = await client.post("/api/v1/auth/refresh")
    assert resp_replay.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_token(client: AsyncClient) -> None:
    """POST /auth/logout clears cookie and revokes token jti."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "logout_test@example.com",
            "username": "logout_test",
            "password": "password123!",
        },
    )
    cookie_val = reg.headers.get("set-cookie", "").split("refresh_token=")[1].split(";")[0]
    client.cookies.set("refresh_token", cookie_val)

    logout_resp = await client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 204

    # Refresh after logout must fail
    refresh_after = await client.post("/api/v1/auth/refresh")
    assert refresh_after.status_code == 401


@pytest.mark.asyncio
async def test_expired_token(client: AsyncClient) -> None:
    """Expired access token returns 401 Unauthorized."""
    import time

    from jose import jwt

    from app.core.config import get_settings

    settings = get_settings()
    now = int(time.time())
    expired_claims = {
        "sub": "1",
        "role": "grower",
        "permissions": ["disease:read"],
        "iat": now - 3600,
        "exp": now - 1800,  # expired 30 mins ago
        "jti": "expired-jti",
        "type": "access",
    }
    expired_jwt = jwt.encode(expired_claims, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_jwt}"})
    assert resp.status_code == 401
    assert "expired" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_inactive_user_forbidden(client: AsyncClient, db_session: AsyncSession) -> None:
    """Inactive user cannot access protected endpoints."""
    from app.repositories.user import UserRepository

    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "inactive@example.com",
            "username": "inactive_user",
            "password": "password123!",
        },
    )
    user_id = reg.json()["user"]["id"]
    token = reg.json()["access_token"]

    # Deactivate user in DB
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_id(user_id)
    assert user is not None
    user.is_active = False
    await db_session.flush()

    # Attempt to access /auth/me with active token but inactive user
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
    assert "inactive" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_legacy_password_verification_and_rehash(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Legacy Werkzeug scrypt hash authenticates and rehashes transparently to Argon2id."""
    import hashlib

    from sqlalchemy import select

    from app.models.auth import Role, User
    from app.repositories.user import UserRepository

    # Werkzeug scrypt hash for 'legacyPassword123!'
    # scrypt:32768:8:1$salt$digest
    salt = b"testlegacy123salt"
    digest = hashlib.scrypt(
        b"legacyPassword123!", salt=salt, n=32768, r=8, p=1, maxmem=128 * 1024 * 1024
    ).hex()
    legacy_hash = f"scrypt:32768:8:1${salt.decode('ascii')}${digest}"

    role_res = await db_session.execute(select(Role).where(Role.name == "grower"))
    role = role_res.scalar_one_or_none()
    if not role:
        role = Role(name="grower", description="Sunflower grower")
        db_session.add(role)
        await db_session.flush()

    legacy_user = User(
        email="legacy_user@example.com",
        username="legacy_user",
        password_hash=legacy_hash,
        role_id=role.id,
        is_active=True,
    )
    db_session.add(legacy_user)
    await db_session.flush()

    # Authenticate with correct password
    resp = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "legacy_user@example.com", "password": "legacyPassword123!"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()

    # Verify that the password_hash was transparently rehashed to Argon2id
    user_repo = UserRepository(db_session)
    reloaded_user = await user_repo.get_by_email("legacy_user@example.com")
    assert reloaded_user is not None
    assert reloaded_user.password_hash.startswith("$argon2")

    # Subsequent login with new argon2 hash still succeeds
    resp2 = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "legacy_user", "password": "legacyPassword123!"},
    )
    assert resp2.status_code == 200
