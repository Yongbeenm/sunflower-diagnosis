"""Idempotent database seeding script.

Seeds:
- 19 atomic permissions per docs/ARCHITECTURE.md § Permissions
- 3 core roles: grower, agronomist, admin with their role_permissions
- 8 symptom categories with sort_order and English/Khmer translations
- Default ruleset version 2026.09.1 (is_active=True, weighted_evidence_v1)
- Initial admin user from environment variables (ADMIN_EMAIL, ADMIN_USERNAME, ADMIN_PASSWORD)

Safe to run repeatedly; changes nothing on subsequent runs.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any

from argon2 import PasswordHasher
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import async_session_factory
from app.models.auth import Permission, Role, RolePermission, User
from app.models.ruleset import Ruleset
from app.models.symptom import SymptomCategory
from app.models.translation import Translation

PERMISSION_DEFS: list[tuple[str, str]] = [
    # Disease
    ("disease:read", "Read published diseases and symptom weights"),
    ("disease:create", "Create new disease entries"),
    ("disease:update", "Update disease details, weights, and translations"),
    ("disease:delete", "Permanently delete diseases from the database"),
    ("disease:publish", "Publish or unpublish diseases"),
    # Symptom
    ("symptom:read", "Read symptoms and categories"),
    ("symptom:create", "Create new symptoms"),
    ("symptom:update", "Update symptom details and translations"),
    ("symptom:delete", "Delete symptoms not associated with active diseases"),
    # Diagnosis
    ("diagnosis:run", "Run sunflower disease diagnosis sessions"),
    ("diagnosis:read_own", "View own past diagnosis session history"),
    ("diagnosis:read_all", "View all growers' diagnosis session history"),
    # Feedback
    ("feedback:create", "Submit diagnosis or general feedback"),
    ("feedback:read", "View submitted feedback items"),
    ("feedback:resolve", "Update feedback status and resolution notes"),
    # Admin / system
    ("user:manage", "Manage user accounts, activation, and assignments"),
    ("rbac:manage", "Manage roles and permission mappings"),
    ("ruleset:manage", "Create, configure, and activate scoring rulesets"),
    ("analytics:read", "View system diagnosis and symptom analytics"),
]

GROWER_PERMISSIONS: set[str] = {
    "disease:read",
    "symptom:read",
    "diagnosis:run",
    "diagnosis:read_own",
    "feedback:create",
}

AGRONOMIST_PERMISSIONS: set[str] = GROWER_PERMISSIONS | {
    "disease:create",
    "disease:update",
    "disease:delete",
    "disease:publish",
    "symptom:create",
    "symptom:update",
    "symptom:delete",
    "diagnosis:read_all",
    "feedback:read",
    "feedback:resolve",
    "analytics:read",
}

ADMIN_PERMISSIONS: set[str] = {code for code, _ in PERMISSION_DEFS}

ROLE_DEFS: list[tuple[str, str, set[str]]] = [
    (
        "grower",
        "Sunflower grower seeking disease diagnoses and management guidance",
        GROWER_PERMISSIONS,
    ),
    (
        "agronomist",
        "Agricultural expert maintaining diseases, symptom weights, and translations",
        AGRONOMIST_PERMISSIONS,
    ),
    ("admin", "System administrator with full operational and RBAC access", ADMIN_PERMISSIONS),
]

CATEGORY_DEFS: list[tuple[str, int, str, str]] = [
    ("leaf", 1, "Leaf", "ស្លឹក"),
    ("leaf_head", 2, "Leaf & Head", "ស្លឹក និងក្បាលផ្កា"),
    ("whole_plant", 3, "Whole Plant", "រុក្ខជាតិទាំងមូល"),
    ("stem", 4, "Stem", "ដើម"),
    ("head", 5, "Head", "ក្បាលផ្កា"),
    ("root", 6, "Root", "ឫស"),
    ("seedling", 7, "Seedling", "កូនដំណាំ"),
    ("environment", 8, "Environment", "បរិស្ថាន"),
]

DEFAULT_RULESET_VERSION = "2026.09.1"
DEFAULT_RULESET_ALGORITHM = "weighted_evidence_v1"
DEFAULT_RULESET_PARAMS: dict[str, Any] = {
    "lambda_absent": 0.5,
    "min_confidence": 0.35,
    "pathognomonic_floor": 0.85,
    "required_missing_penalty": 0.25,
}


async def seed_permissions(session: AsyncSession) -> dict[str, Permission]:
    """Upsert atomic permissions."""
    result = await session.execute(select(Permission))
    existing = {p.code: p for p in result.scalars().all()}

    for code, desc in PERMISSION_DEFS:
        if code not in existing:
            perm = Permission(code=code, description=desc)
            session.add(perm)
            existing[code] = perm
        else:
            existing[code].description = desc

    await session.flush()
    return existing


async def seed_roles(
    session: AsyncSession,
    permissions: dict[str, Permission],
) -> dict[str, Role]:
    """Upsert roles and map role permissions."""
    result = await session.execute(select(Role))
    existing_roles = {r.name: r for r in result.scalars().all()}

    for name, desc, perm_codes in ROLE_DEFS:
        if name not in existing_roles:
            role = Role(name=name, description=desc)
            session.add(role)
            await session.flush()
            existing_roles[name] = role
        else:
            role = existing_roles[name]
            role.description = desc

        # Check existing role permissions
        rp_res = await session.execute(
            select(RolePermission.permission_id).where(RolePermission.role_id == role.id)
        )
        existing_perm_ids = set(rp_res.scalars().all())

        for code in perm_codes:
            perm = permissions[code]
            if perm.id not in existing_perm_ids:
                session.add(RolePermission(role_id=role.id, permission_id=perm.id))

    await session.flush()
    return existing_roles


async def seed_categories(session: AsyncSession) -> None:
    """Upsert symptom categories with English and Khmer translations."""
    result = await session.execute(select(SymptomCategory))
    existing_cats = {c.code: c for c in result.scalars().all()}

    for code, sort_order, en_label, km_label in CATEGORY_DEFS:
        if code not in existing_cats:
            cat = SymptomCategory(code=code, sort_order=sort_order)
            session.add(cat)
            await session.flush()
            existing_cats[code] = cat
        else:
            cat = existing_cats[code]
            cat.sort_order = sort_order

        # Translations for label
        for locale, val in [("en", en_label), ("km", km_label)]:
            t_res = await session.execute(
                select(Translation).where(
                    Translation.entity_type == "category",
                    Translation.entity_id == cat.id,
                    Translation.locale == locale,
                    Translation.field == "label",
                )
            )
            trans = t_res.scalar_one_or_none()
            if trans is None:
                session.add(
                    Translation(
                        entity_type="category",
                        entity_id=cat.id,
                        locale=locale,
                        field="label",
                        value=val,
                    )
                )
            else:
                trans.value = val

    await session.flush()


async def seed_ruleset(session: AsyncSession) -> None:
    """Upsert default active ruleset."""
    result = await session.execute(
        select(Ruleset).where(Ruleset.version == DEFAULT_RULESET_VERSION)
    )
    ruleset = result.scalar_one_or_none()

    if ruleset is None:
        ruleset = Ruleset(
            version=DEFAULT_RULESET_VERSION,
            algorithm=DEFAULT_RULESET_ALGORITHM,
            params=DEFAULT_RULESET_PARAMS,
            is_active=True,
        )
        session.add(ruleset)
    else:
        ruleset.algorithm = DEFAULT_RULESET_ALGORITHM
        ruleset.params = DEFAULT_RULESET_PARAMS
        ruleset.is_active = True

    await session.flush()


async def seed_admin(session: AsyncSession, admin_role: Role) -> None:
    """Create default admin user if not existing or reset its password and role. Refuses if ADMIN_PASSWORD is empty."""
    settings = get_settings()
    if not settings.ADMIN_PASSWORD:
        raise RuntimeError("ADMIN_PASSWORD environment variable is empty. Refusing to seed admin.")

    result = await session.execute(
        select(User).where(
            (User.email == settings.ADMIN_EMAIL) | (User.username == settings.ADMIN_USERNAME)
        )
    )
    admin_user = result.scalar_one_or_none()

    ph = PasswordHasher()
    hashed = ph.hash(settings.ADMIN_PASSWORD)

    if admin_user is None:
        admin_user = User(
            email=settings.ADMIN_EMAIL,
            username=settings.ADMIN_USERNAME,
            password_hash=hashed,
            role_id=admin_role.id,
            is_active=True,
        )
        session.add(admin_user)
    else:
        admin_user.email = settings.ADMIN_EMAIL
        admin_user.username = settings.ADMIN_USERNAME
        admin_user.password_hash = hashed
        admin_user.role_id = admin_role.id
        admin_user.is_active = True

    await session.flush()


async def seed_database(session: AsyncSession) -> None:
    """Run all idempotent seed steps within a transaction."""
    perms = await seed_permissions(session)
    roles = await seed_roles(session, perms)
    await seed_categories(session)
    await seed_ruleset(session)
    await seed_admin(session, roles["admin"])
    await session.commit()


async def main() -> None:
    """CLI entry point for running the seeder."""
    async with async_session_factory() as session:
        await seed_database(session)
    print("Database seeding completed successfully.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"Error seeding database: {exc}", file=sys.stderr)
        sys.exit(1)
