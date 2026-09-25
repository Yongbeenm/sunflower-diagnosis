"""Audit repository for recording immutable change trails."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


class AuditRepository:
    """Database persistence for audit log entries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log_action(
        self,
        actor_id: int | None,
        action: str,
        entity_type: str,
        entity_id: int | None,
        diff: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Create and flush an audit trail entry."""
        entry = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            diff=diff,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry
