"""Admin repository for RBAC, users, and ruleset persistence."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.auth import Permission, Role, User
from app.models.ruleset import Ruleset


class AdminRepository:
    """Repository handling administration queries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # -----------------------------------------------------------------------
    # Roles & Permissions
    # -----------------------------------------------------------------------

    async def get_roles(self) -> list[Role]:
        """Fetch all roles with loaded permissions."""
        stmt = select(Role).options(selectinload(Role.permissions)).order_by(Role.id.asc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_permissions(self) -> list[Permission]:
        """Fetch all system permissions."""
        stmt = select(Permission).order_by(Permission.code.asc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_role_by_id(self, role_id: int) -> Role | None:
        """Fetch single role by ID."""
        stmt = select(Role).where(Role.id == role_id).options(selectinload(Role.permissions))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def set_role_permissions(self, role_id: int, permission_codes: list[str]) -> Role:
        """Replace all permissions for a role in one transaction."""
        role = await self.get_role_by_id(role_id)
        assert role is not None

        stmt = select(Permission).where(Permission.code.in_(permission_codes))
        res = await self.session.execute(stmt)
        permissions = list(res.scalars().all())

        role.permissions = permissions
        await self.session.flush()
        return role

    # -----------------------------------------------------------------------
    # Users
    # -----------------------------------------------------------------------

    async def list_users(self, page: int = 1, size: int = 20) -> tuple[list[User], int]:
        """List user accounts paginated."""
        count_stmt = select(func.count(User.id))
        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(User)
            .options(selectinload(User.role))
            .order_by(User.id.asc())
            .offset((page - 1) * size)
            .limit(size)
        )
        res = await self.session.execute(stmt)
        users = list(res.scalars().all())
        return users, total

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Fetch single user by ID with role loaded."""
        stmt = select(User).where(User.id == user_id).options(selectinload(User.role))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_user(
        self,
        user: User,
        role_id: int | None = None,
        is_active: bool | None = None,
    ) -> User:
        """Update user role and active state."""
        if role_id is not None:
            user.role_id = role_id
        if is_active is not None:
            user.is_active = is_active

        await self.session.flush()
        return user

    # -----------------------------------------------------------------------
    # Rulesets
    # -----------------------------------------------------------------------

    async def list_rulesets(self) -> list[Ruleset]:
        """List all rulesets ordered by version."""
        stmt = (
            select(Ruleset).options(selectinload(Ruleset.published_by)).order_by(Ruleset.id.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_ruleset_by_id(self, ruleset_id: int) -> Ruleset | None:
        """Fetch ruleset by ID."""
        stmt = (
            select(Ruleset)
            .where(Ruleset.id == ruleset_id)
            .options(selectinload(Ruleset.published_by))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def activate_ruleset(self, ruleset_id: int, user_id: int) -> Ruleset:
        """Atomically deactivate all rulesets and activate the target one."""
        # Deactivate all
        await self.session.execute(update(Ruleset).values(is_active=False))

        # Activate target
        now = datetime.now(UTC)
        target = await self.get_ruleset_by_id(ruleset_id)
        assert target is not None

        target.is_active = True
        target.published_at = now
        target.published_by_id = user_id

        await self.session.flush()
        return target
