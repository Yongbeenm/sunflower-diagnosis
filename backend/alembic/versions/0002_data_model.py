"""Create complete data model schema.

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-19
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None

pathogen_type_enum = sa.Enum(
    "fungal",
    "bacterial",
    "viral",
    "abiotic",
    "other",
    name="pathogen_type",
)
diagnosis_outcome_enum = sa.Enum(
    "matched",
    "no_match",
    name="diagnosis_outcome",
)
diagnosis_answer_enum = sa.Enum(
    "yes",
    "no",
    "unknown",
    name="diagnosis_answer",
)
feedback_status_enum = sa.Enum(
    "open",
    "in_review",
    "resolved",
    name="feedback_status",
)


def upgrade() -> None:
    json_type = sa.JSON().with_variant(postgresql.JSONB, "postgresql")

    # 1. roles
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_roles")),
        sa.UniqueConstraint("name", name=op.f("uq_roles_name")),
    )
    op.create_index(op.f("ix_roles_name"), "roles", ["name"], unique=True)

    # 2. permissions
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_permissions")),
        sa.UniqueConstraint("code", name=op.f("uq_permissions_code")),
    )
    op.create_index(op.f("ix_permissions_code"), "permissions", ["code"], unique=True)

    # 3. role_permissions
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            name=op.f("fk_role_permissions_permission_id_permissions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name=op.f("fk_role_permissions_role_id_roles"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("role_id", "permission_id", name=op.f("pk_role_permissions")),
    )

    # 4. users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], name=op.f("fk_users_role_id_roles")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    # 5. symptom_categories
    op.create_table(
        "symptom_categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_symptom_categories")),
        sa.UniqueConstraint("code", name=op.f("uq_symptom_categories_code")),
    )
    op.create_index(op.f("ix_symptom_categories_code"), "symptom_categories", ["code"], unique=True)

    # 6. media
    op.create_table(
        "media",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("storage_key", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=128), nullable=False),
        sa.Column("bytes", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("uploaded_by_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by_id"],
            ["users.id"],
            name=op.f("fk_media_uploaded_by_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_media")),
        sa.UniqueConstraint("storage_key", name=op.f("uq_media_storage_key")),
    )
    op.create_index(op.f("ix_media_storage_key"), "media", ["storage_key"], unique=True)

    # 7. symptoms
    op.create_table(
        "symptoms",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("is_environmental", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["symptom_categories.id"],
            name=op.f("fk_symptoms_category_id_symptom_categories"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
            name=op.f("fk_symptoms_created_by_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
            name=op.f("fk_symptoms_updated_by_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_symptoms")),
        sa.UniqueConstraint("code", name=op.f("uq_symptoms_code")),
    )
    op.create_index(op.f("ix_symptoms_code"), "symptoms", ["code"], unique=True)

    # 8. diseases
    op.create_table(
        "diseases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("pathogen_type", pathogen_type_enum, nullable=False),
        sa.Column("image_media_id", sa.Integer(), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
            name=op.f("fk_diseases_created_by_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["image_media_id"],
            ["media.id"],
            name=op.f("fk_diseases_image_media_id_media"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
            name=op.f("fk_diseases_updated_by_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_diseases")),
        sa.UniqueConstraint("slug", name=op.f("uq_diseases_slug")),
    )
    op.create_index(op.f("ix_diseases_slug"), "diseases", ["slug"], unique=True)

    # 9. disease_symptoms
    op.create_table(
        "disease_symptoms",
        sa.Column("disease_id", sa.Integer(), nullable=False),
        sa.Column("symptom_id", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("is_pathognomonic", sa.Boolean(), nullable=False),
        sa.CheckConstraint(
            "weight >= 0 AND weight <= 1",
            name=op.f("ck_disease_symptoms_ck_disease_symptoms_weight_range"),
        ),
        sa.ForeignKeyConstraint(
            ["disease_id"],
            ["diseases.id"],
            name=op.f("fk_disease_symptoms_disease_id_diseases"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["symptom_id"],
            ["symptoms.id"],
            name=op.f("fk_disease_symptoms_symptom_id_symptoms"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("disease_id", "symptom_id", name=op.f("pk_disease_symptoms")),
    )

    # 10. translations
    op.create_table(
        "translations",
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(length=10), nullable=False),
        sa.Column("field", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint(
            "entity_type",
            "entity_id",
            "locale",
            "field",
            name=op.f("pk_translations"),
        ),
    )
    op.create_index(
        "ix_translations_lookup",
        "translations",
        ["entity_type", "entity_id", "locale"],
        unique=False,
    )

    # 11. rulesets
    op.create_table(
        "rulesets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("algorithm", sa.String(length=64), nullable=False),
        sa.Column("params", json_type, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["published_by_id"],
            ["users.id"],
            name=op.f("fk_rulesets_published_by_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rulesets")),
        sa.UniqueConstraint("version", name=op.f("uq_rulesets_version")),
    )
    op.create_index(op.f("ix_rulesets_version"), "rulesets", ["version"], unique=True)
    op.create_index(
        "uq_rulesets_single_active",
        "rulesets",
        ["is_active"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
        sqlite_where=sa.text("is_active = 1"),
    )

    # 12. diagnosis_sessions
    op.create_table(
        "diagnosis_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("ruleset_id", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(length=10), nullable=False),
        sa.Column("symptom_count", sa.Integer(), nullable=False),
        sa.Column("top_disease_id", sa.Integer(), nullable=True),
        sa.Column("top_confidence", sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column("outcome", diagnosis_outcome_enum, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["ruleset_id"],
            ["rulesets.id"],
            name=op.f("fk_diagnosis_sessions_ruleset_id_rulesets"),
        ),
        sa.ForeignKeyConstraint(
            ["top_disease_id"],
            ["diseases.id"],
            name=op.f("fk_diagnosis_sessions_top_disease_id_diseases"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_diagnosis_sessions_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_diagnosis_sessions")),
    )
    op.create_index(
        "ix_diagnosis_sessions_user_created",
        "diagnosis_sessions",
        ["user_id", sa.text("created_at DESC")],
        unique=False,
    )

    # 13. diagnosis_selected_symptoms
    op.create_table(
        "diagnosis_selected_symptoms",
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("symptom_id", sa.Integer(), nullable=False),
        sa.Column("answer", diagnosis_answer_enum, nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["diagnosis_sessions.id"],
            name=op.f("fk_diagnosis_selected_symptoms_session_id_diagnosis_sessions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["symptom_id"],
            ["symptoms.id"],
            name=op.f("fk_diagnosis_selected_symptoms_symptom_id_symptoms"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "session_id",
            "symptom_id",
            name=op.f("pk_diagnosis_selected_symptoms"),
        ),
    )

    # 14. diagnosis_results
    op.create_table(
        "diagnosis_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("disease_id", sa.Integer(), nullable=True),
        sa.Column("disease_name_snapshot", sa.String(length=255), nullable=False),
        sa.Column("score", sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column("evidence", json_type, nullable=False),
        sa.ForeignKeyConstraint(
            ["disease_id"],
            ["diseases.id"],
            name=op.f("fk_diagnosis_results_disease_id_diseases"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["diagnosis_sessions.id"],
            name=op.f("fk_diagnosis_results_session_id_diagnosis_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_diagnosis_results")),
    )

    # 15. feedback
    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("diagnosis_session_id", sa.Uuid(), nullable=True),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("media_id", sa.Integer(), nullable=True),
        sa.Column("status", feedback_status_enum, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["diagnosis_session_id"],
            ["diagnosis_sessions.id"],
            name=op.f("fk_feedback_diagnosis_session_id_diagnosis_sessions"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["media_id"],
            ["media.id"],
            name=op.f("fk_feedback_media_id_media"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_feedback_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_feedback")),
    )
    op.create_index(
        "ix_feedback_status_created",
        "feedback",
        ["status", sa.text("created_at DESC")],
        unique=False,
    )

    # 16. audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("diff", json_type, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["users.id"],
            name=op.f("fk_audit_log_actor_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_log")),
    )
    op.create_index(op.f("ix_audit_log_action"), "audit_log", ["action"], unique=False)
    op.create_index(op.f("ix_audit_log_entity_type"), "audit_log", ["entity_type"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    # Drop in reverse dependency order
    op.drop_table("audit_log")
    op.drop_table("feedback")
    op.drop_table("diagnosis_results")
    op.drop_table("diagnosis_selected_symptoms")
    op.drop_table("diagnosis_sessions")
    op.drop_table("rulesets")
    op.drop_table("translations")
    op.drop_table("disease_symptoms")
    op.drop_table("diseases")
    op.drop_table("symptoms")
    op.drop_table("media")
    op.drop_table("symptom_categories")
    op.drop_table("users")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")

    if is_postgres:
        feedback_status_enum.drop(bind, checkfirst=True)
        diagnosis_answer_enum.drop(bind, checkfirst=True)
        diagnosis_outcome_enum.drop(bind, checkfirst=True)
        pathogen_type_enum.drop(bind, checkfirst=True)
