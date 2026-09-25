"""Add full-text search tsvector column and GIN index to diseases.

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-20
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    # 1. Add search_vector column to diseases
    if is_postgres:
        op.add_column("diseases", sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True))
        op.create_index(
            "ix_diseases_search_vector",
            "diseases",
            ["search_vector"],
            postgresql_using="gin",
        )

        # 2. Trigger function to update search_vector from translations
        op.execute(
            """
            CREATE OR REPLACE FUNCTION fn_update_disease_search_vector()
            RETURNS TRIGGER AS $$
            DECLARE
                target_disease_id INT;
            BEGIN
                IF TG_OP = 'DELETE' THEN
                    target_disease_id := OLD.entity_id;
                ELSE
                    target_disease_id := NEW.entity_id;
                END IF;

                IF (TG_OP = 'DELETE' AND OLD.entity_type = 'disease')
                   OR (TG_OP <> 'DELETE' AND NEW.entity_type = 'disease') THEN
                    UPDATE diseases
                    SET search_vector = (
                        SELECT setweight(to_tsvector('simple',
                               coalesce(string_agg(
                                   CASE WHEN field = 'name' THEN value END, ' '
                               ), '')), 'A') ||
                               setweight(to_tsvector('simple',
                               coalesce(string_agg(
                                   CASE WHEN field = 'description' THEN value END, ' '
                               ), '')), 'B')
                        FROM translations
                        WHERE entity_type = 'disease' AND entity_id = target_disease_id
                    )
                    WHERE id = target_disease_id;
                END IF;

                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;
            """
        )

        # 3. Create trigger on translations table
        op.execute(
            """
            CREATE TRIGGER trg_translations_search_vector
            AFTER INSERT OR UPDATE OR DELETE ON translations
            FOR EACH ROW
            EXECUTE FUNCTION fn_update_disease_search_vector();
            """
        )
    else:
        # SQLite fallback for test environments
        op.add_column("diseases", sa.Column("search_vector", sa.Text(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        op.execute("DROP TRIGGER IF EXISTS trg_translations_search_vector ON translations;")
        op.execute("DROP FUNCTION IF EXISTS fn_update_disease_search_vector();")
        op.drop_index("ix_diseases_search_vector", table_name="diseases")

    op.drop_column("diseases", "search_vector")
