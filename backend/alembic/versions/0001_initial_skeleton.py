"""Initial skeleton revision.

No tables exist yet — models are added in Step 2. This revision establishes
the Alembic version table and confirms the migration chain is working.

Revision ID: 0001
Revises: (base)
Create Date: 2026-09-19
"""

from __future__ import annotations

from alembic import op  # noqa: F401

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # No schema changes yet — models are introduced in Step 2.
    pass


def downgrade() -> None:
    pass
