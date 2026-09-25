"""Smoke tests for the /health endpoint."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_ok(client: AsyncClient) -> None:
    """GET /health must return 200 with status='ok'."""
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "0.1.0"
    # db field may be "down" in the test environment (SQLite ping), that's fine.
    assert body["db"] in {"up", "down"}


@pytest.mark.asyncio
async def test_health_has_request_id_header(client: AsyncClient) -> None:
    """Every response must carry an X-Request-Id header."""
    response = await client.get("/health")
    assert "x-request-id" in response.headers
