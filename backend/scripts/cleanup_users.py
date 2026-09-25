"""Clean up database users - keep only admin, expert, and one normal user.

This script:
1. Removes all users except admin
2. Creates/updates an expert (agronomist) user
3. Creates/updates a normal (grower) user
4. Sets passwords to: admin, expert, user
"""

from __future__ import annotations

import asyncio
import sys

from argon2 import PasswordHasher
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import async_session_factory
from app.models.auth import Role, User

ph = PasswordHasher()


async def cleanup_users(session: AsyncSession) -> None:
    """Remove old users and create/update admin, expert, and user accounts."""
    
    # Fetch roles
    roles_result = await session.execute(select(Role))
    roles = {r.name: r for r in roles_result.scalars().all()}
    
    if not all(k in roles for k in ["admin", "agronomist", "grower"]):
        print("❌ Required roles not found. Run scripts/seed.py first.")
        sys.exit(1)
    
    admin_role = roles["admin"]
    agronomist_role = roles["agronomist"]
    grower_role = roles["grower"]
    
    # Get current users
    users_result = await session.execute(select(User))
    existing_users = {u.username: u for u in users_result.scalars().all()}
    
    print(f"📊 Found {len(existing_users)} existing user(s)")
    
    # Define target users
    target_users = {
        "admin": {
            "email": "admin@example.com",
            "username": "admin",
            "password": "admin",
            "role": admin_role,
        },
        "expert": {
            "email": "expert@example.com",
            "username": "expert",
            "password": "expert",
            "role": agronomist_role,
        },
        "user": {
            "email": "user@example.com",
            "username": "user",
            "password": "user",
            "role": grower_role,
        },
    }
    
    # Delete all users NOT in target list
    users_to_keep = {"admin", "expert", "user"}
    users_to_delete = [u for u in existing_users if u not in users_to_keep]
    
    if users_to_delete:
        print(f"🗑️  Deleting {len(users_to_delete)} old user(s): {', '.join(users_to_delete)}")
        await session.execute(
            delete(User).where(User.username.in_(users_to_delete))
        )
    
    # Create or update target users
    for username, user_data in target_users.items():
        if username in existing_users:
            # Update existing user
            user = existing_users[username]
            user.email = user_data["email"]
            user.password_hash = ph.hash(user_data["password"])
            user.role_id = user_data["role"].id
            user.is_active = True
            print(f"✏️  Updated user: {username} (password: {user_data['password']})")
        else:
            # Create new user
            user = User(
                email=user_data["email"],
                username=username,
                password_hash=ph.hash(user_data["password"]),
                role_id=user_data["role"].id,
                is_active=True,
            )
            session.add(user)
            print(f"✅ Created user: {username} (password: {user_data['password']})")
    
    await session.commit()
    print("\n✅ User cleanup complete!")
    print("\n📝 Login credentials:")
    print("   Admin:  username=admin  password=admin")
    print("   Expert: username=expert password=expert")
    print("   User:   username=user   password=user")


async def main() -> None:
    settings = get_settings()
    
    print("🧹 Sunflower User Cleanup Script")
    print("=" * 60)
    print(f"Database: {settings.DATABASE_URL.split('@')[-1]}")
    print()
    
    confirm = input("⚠️  This will DELETE all users except admin, expert, and user.\nContinue? [y/N]: ")
    if confirm.lower() != "y":
        print("❌ Cancelled")
        sys.exit(0)
    
    async with async_session_factory() as session:
        await cleanup_users(session)


if __name__ == "__main__":
    asyncio.run(main())
