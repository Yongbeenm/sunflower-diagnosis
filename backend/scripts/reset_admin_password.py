"""Explicitly reset the admin user to admin@example.com with the password from settings or command line argument."""
from __future__ import annotations

import asyncio
import sys

from argon2 import PasswordHasher
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import async_session_factory
from app.models.auth import Role, User, Permission, RolePermission


async def reset_admin(session: AsyncSession) -> None:
    settings = get_settings()
    email = settings.ADMIN_EMAIL or "admin@example.com"
    username = settings.ADMIN_USERNAME or "admin"
    password = settings.ADMIN_PASSWORD or "leetaka!1234568"

    print(f"🔧 Resetting admin user: {email} / {username}")

    # Ensure admin role exists
    result = await session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one_or_none()
    if not admin_role:
        print("Creating admin role...")
        admin_role = Role(name="admin", description="Full system administrator")
        session.add(admin_role)
        await session.flush()

    # Ensure all permissions are granted to admin role
    all_perms_res = await session.execute(select(Permission))
    all_perms = all_perms_res.scalars().all()
    
    role_perms_res = await session.execute(
        select(RolePermission).where(RolePermission.role_id == admin_role.id)
    )
    existing_perm_ids = {rp.permission_id for rp in role_perms_res.scalars().all()}
    
    for perm in all_perms:
        if perm.id not in existing_perm_ids:
            session.add(RolePermission(role_id=admin_role.id, permission_id=perm.id))

    ph = PasswordHasher()
    hashed = ph.hash(password)

    user_res = await session.execute(
        select(User).where((User.email == email) | (User.username == username))
    )
    admin_user = user_res.scalar_one_or_none()

    if admin_user is None:
        admin_user = User(
            email=email,
            username=username,
            password_hash=hashed,
            role_id=admin_role.id,
            is_active=True,
        )
        session.add(admin_user)
        print(f"✅ Created admin user: {email} (username: {username})")
    else:
        admin_user.email = email
        admin_user.username = username
        admin_user.password_hash = hashed
        admin_user.role_id = admin_role.id
        admin_user.is_active = True
        print(f"✅ Updated existing admin user: {email} (username: {username})")

    await session.commit()
    print("=" * 50)
    print("🎉 Admin user credentials:")
    print(f"   Email:    {email}")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   Role:     admin (with all permissions)")
    print("=" * 50)


async def main() -> None:
    async with async_session_factory() as session:
        await reset_admin(session)


if __name__ == "__main__":
    asyncio.run(main())

