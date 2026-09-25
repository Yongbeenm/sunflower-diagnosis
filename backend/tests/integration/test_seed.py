"""Integration test verifying database seed idempotency."""

from __future__ import annotations

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import Permission, Role, RolePermission, User
from app.models.ruleset import Ruleset
from app.models.symptom import SymptomCategory
from app.models.translation import Translation
from scripts.seed import seed_database


@pytest.mark.asyncio
async def test_seed_is_idempotent(db_session: AsyncSession) -> None:
    """Running seed_database twice results in identical row counts and state."""
    # First seed run
    await seed_database(db_session)

    async def get_counts() -> dict[str, int]:
        p_count = (
            await db_session.execute(select(func.count()).select_from(Permission))
        ).scalar_one()
        r_count = (await db_session.execute(select(func.count()).select_from(Role))).scalar_one()
        rp_count = (
            await db_session.execute(select(func.count()).select_from(RolePermission))
        ).scalar_one()
        c_count = (
            await db_session.execute(select(func.count()).select_from(SymptomCategory))
        ).scalar_one()
        t_count = (
            await db_session.execute(select(func.count()).select_from(Translation))
        ).scalar_one()
        rs_count = (
            await db_session.execute(select(func.count()).select_from(Ruleset))
        ).scalar_one()
        u_count = (await db_session.execute(select(func.count()).select_from(User))).scalar_one()

        return {
            "permissions": p_count,
            "roles": r_count,
            "role_permissions": rp_count,
            "categories": c_count,
            "translations": t_count,
            "rulesets": rs_count,
            "users": u_count,
        }

    counts_after_first = await get_counts()

    # Verify baseline seeded expectations
    assert counts_after_first["permissions"] == 19
    assert counts_after_first["roles"] == 3
    assert counts_after_first["categories"] == 8
    assert counts_after_first["translations"] == 16  # 8 en + 8 km category labels
    assert counts_after_first["rulesets"] == 1
    assert counts_after_first["users"] >= 1

    # Second seed run
    await seed_database(db_session)

    counts_after_second = await get_counts()

    # Exact equality across all tables
    assert counts_after_second == counts_after_first
