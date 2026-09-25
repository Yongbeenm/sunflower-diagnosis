"""Security utilities: password hashing, verification, and JWT management."""

from __future__ import annotations

import contextlib
import hashlib
import hmac
import time
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import get_settings
from app.core.errors import UnauthorizedError

_ph = PasswordHasher()

# Pre-computed dummy hash to prevent timing attacks / user enumeration
_DUMMY_HASH: str = _ph.hash("sunflower-dummy-timing-password")


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    return _ph.hash(password)


def is_legacy_hash(hashed: str) -> bool:
    """Return True if the hash string is in a legacy format (Werkzeug scrypt/pbkdf2)."""
    return hashed.startswith("scrypt:") or hashed.startswith("pbkdf2:")


def _verify_legacy_hash(password: str, hashed: str) -> bool:
    """Verify password against Werkzeug scrypt or pbkdf2 hash format using standard library."""
    try:
        if hashed.startswith("scrypt:"):
            parts = hashed.split("$")
            if len(parts) != 3:
                return False
            method_params = parts[0].split(":")
            n = int(method_params[1])
            r = int(method_params[2])
            p = int(method_params[3])
            salt = parts[1].encode("utf-8")
            target_digest = bytes.fromhex(parts[2])
            derived = hashlib.scrypt(
                password.encode("utf-8"),
                salt=salt,
                n=n,
                r=r,
                p=p,
                maxmem=128 * 1024 * 1024,
            )
            return hmac.compare_digest(derived, target_digest)
        if hashed.startswith("pbkdf2:"):
            parts = hashed.split("$")
            if len(parts) != 3:
                return False
            method_params = parts[0].split(":")
            hash_name = method_params[1]
            iterations = int(method_params[2])
            salt = parts[1].encode("utf-8")
            target_digest = bytes.fromhex(parts[2])
            derived = hashlib.pbkdf2_hmac(
                hash_name,
                password.encode("utf-8"),
                salt,
                iterations,
            )
            return hmac.compare_digest(derived, target_digest)
        return False
    except Exception:
        return False


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against an Argon2id hash or legacy Werkzeug hash."""
    if is_legacy_hash(hashed):
        return _verify_legacy_hash(password, hashed)
    try:
        return _ph.verify(hashed, password)
    except (VerifyMismatchError, Exception):
        return False


def verify_dummy_password(password: str) -> None:
    """Run a real Argon2 verify against a dummy hash to keep timing constant on unknown accounts."""
    with contextlib.suppress(Exception):
        _ph.verify(_DUMMY_HASH, password)


class RefreshTokenStore:
    """In-memory store for tracking revoked refresh tokens.

    Can be replaced with Redis in production.
    """

    def __init__(self) -> None:
        # Stores revoked refresh token jtis
        self._revoked_tokens: set[str] = set()

    def register(self, jti: str, user_id: int) -> None:
        """Register active token (no-op with revocation-based model)."""
        pass

    def is_valid(self, jti: str) -> bool:
        """Return True if the jti has not been explicitly revoked."""
        return jti not in self._revoked_tokens

    def revoke(self, jti: str) -> None:
        """Revoke a jti so it cannot be reused."""
        self._revoked_tokens.add(jti)


token_store = RefreshTokenStore()


def create_access_token(user_id: int, role: str, permissions: list[str]) -> tuple[str, str]:
    """Create a short-lived access token containing user permissions.

    Returns:
        (access_token_str, jti)
    """
    settings = get_settings()
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=settings.ACCESS_TTL_MIN)
    token_jti = str(uuid.uuid4())

    claims: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "permissions": permissions,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": token_jti,
        "type": "access",
    }

    token = jwt.encode(claims, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    return token, token_jti


def create_refresh_token(user_id: int) -> tuple[str, str]:
    """Create a long-lived refresh token with unique jti.

    Returns:
        (refresh_token_str, jti)
    """
    settings = get_settings()
    now = datetime.now(UTC)
    expires_at = now + timedelta(days=settings.REFRESH_TTL_DAYS)
    token_jti = str(uuid.uuid4())

    claims: dict[str, Any] = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": token_jti,
        "type": "refresh",
    }

    token = jwt.encode(claims, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    token_store.register(token_jti, user_id)
    return token, token_jti


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token's signature and expiration."""
    settings = get_settings()
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
        )
        exp = payload.get("exp")
        if exp is not None and exp < time.time():
            raise UnauthorizedError(detail="Token has expired")
        return payload
    except UnauthorizedError:
        raise
    except ExpiredSignatureError as exc:
        raise UnauthorizedError(detail="Token has expired") from exc
    except JWTError as exc:
        raise UnauthorizedError(detail="Invalid token") from exc
