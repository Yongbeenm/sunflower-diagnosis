"""Audit service providing helpers to record mutations."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.repositories.audit import AuditRepository


class AuditService:
    """Service to record audit logs for resource mutations."""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = AuditRepository(session)

    async def record(
        self,
        actor_id: int | None,
        action: str,
        entity_type: str,
        entity_id: int | None,
        diff: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Record an audit trail event."""
        return await self.repository.log_action(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            diff=diff,
        )
