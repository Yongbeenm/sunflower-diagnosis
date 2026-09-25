"""Create additional user accounts (agronomist/grower)."""

from __future__ import annotations

import asyncio
import sys

from argon2 import PasswordHasher
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models.auth import Role, User

USERS = [
    {
        "email": "expert@example.com",
        "username": "expert",
        "password": "expert123",
        "role": "agronomist",
    },
    {
        "email": "grower@example.com",
        "username": "grower",
        "password": "grower123",
        "role": "grower",
    },
]


async def create_users(session: AsyncSession) -> None:
    """Create sample users."""
    print("👤 Creating user accounts...")
    print()

    # Get roles
    result = await session.execute(select(Role))
    roles = {role.name: role for role in result.scalars().all()}

    ph = PasswordHasher()

    for user_data in USERS:
        # Check if user exists
        result = await session.execute(
            select(User).where(
                (User.email == user_data["email"]) | (User.username == user_data["username"])
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"  ⚠️  User {user_data['username']} already exists")
            continue

        role = roles[user_data["role"]]
        hashed = ph.hash(user_data["password"])

        user = User(
            email=user_data["email"],
            username=user_data["username"],
            password_hash=hashed,
            role_id=role.id,
            is_active=True,
        )
        session.add(user)
        print(f"  ✓ Created {user_data['role']}: {user_data['username']}")

    await session.commit()
    print()
    print("✅ Users created!")
    print()
    print("Login credentials:")
    print("-" * 50)
    for user_data in USERS:
        print(f"{user_data['role'].upper()}:")
        print(f"  Username: {user_data['username']}")
        print(f"  Password: {user_data['password']}")
        print()


async def main() -> None:
    """CLI entry point."""
    async with async_session_factory() as session:
        await create_users(session)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"❌ Error: {exc}", file=sys.stderr)
        sys.exit(1)
