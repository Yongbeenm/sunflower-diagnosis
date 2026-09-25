"""
Quick script to fix missing permissions by re-running the seed.
Can be run on production database via environment variables.
"""
import asyncio
import sys

from app.db.session import async_session_factory
from scripts.seed import seed_database


async def main() -> None:
    """Re-run seed to add missing permissions and role mappings."""
    print("🔧 Fixing permissions and role mappings...")
    async with async_session_factory() as session:
        await seed_database(session)
    print("✅ Permissions fixed successfully!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"❌ Error: {exc}", file=sys.stderr)
        sys.exit(1)
