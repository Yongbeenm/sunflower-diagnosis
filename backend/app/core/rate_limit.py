"""Rate limiting interface and in-memory sliding window implementation."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Protocol

from fastapi import status

from app.core.errors import AppError


class RateLimitExceededError(AppError):
    """Raised when request rate exceeds allowed limits."""

    status = status.HTTP_429_TOO_MANY_REQUESTS
    title = "Rate Limit Exceeded"
    type_uri = "/errors/rate-limit-exceeded"


class RateLimiter(Protocol):
    """Abstract interface for rate limiting."""

    def check_and_record(self, key: str, max_attempts: int, window_seconds: int) -> None:
        """Record attempt for key and raise RateLimitExceededError if limit breached."""
        ...


class InMemoryRateLimiter:
    """Sliding-window in-memory rate limiter."""

    def __init__(self) -> None:
        # key -> list of timestamp floats
        self._attempts: dict[str, list[float]] = defaultdict(list)

    def check_and_record(self, key: str, max_attempts: int, window_seconds: int) -> None:
        now = time.time()
        cutoff = now - window_seconds
        attempts = [t for t in self._attempts[key] if t > cutoff]

        if len(attempts) >= max_attempts:
            raise RateLimitExceededError(
                detail=f"Too many attempts. Please try again after {window_seconds // 60} minutes."
            )

        attempts.append(now)
        self._attempts[key] = attempts

    def reset(self, key: str | None = None) -> None:
        """Reset attempts (useful for testing)."""
        if key is not None:
            self._attempts.pop(key, None)
        else:
            self._attempts.clear()


login_rate_limiter = InMemoryRateLimiter()
