"""User repository with explicit relationship loading."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.auth import Role, User


class UserRepository:
    """Database operations for User entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        """Fetch user by id with eager loaded role and permissions."""
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.role).selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Fetch user by email with eager loaded role and permissions."""
        stmt = (
            select(User)
            .where(User.email == email)
            .options(selectinload(User.role).selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Fetch user by username with eager loaded role and permissions."""
        stmt = (
            select(User)
            .where(User.username == username)
            .options(selectinload(User.role).selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_identifier(self, identifier: str) -> User | None:
        """Fetch user by email or username with eager loaded role and permissions."""
        stmt = (
            select(User)
            .where((User.email == identifier) | (User.username == identifier))
            .options(selectinload(User.role).selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_role_by_name(self, name: str) -> Role | None:
        """Fetch role by name."""
        stmt = select(Role).where(Role.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Add user to session and flush."""
        self.session.add(user)
        await self.session.flush()
        # Re-fetch with loaded role and permissions
        created = await self.get_by_id(user.id)
        assert created is not None
        return created
