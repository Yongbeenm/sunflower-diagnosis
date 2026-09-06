from __future__ import annotations

from sqlalchemy import inspect, text

from extensions import db


def _table_columns(table_name: str) -> set[str]:
    inspector = inspect(db.engine)
    if table_name not in inspector.get_table_names():
        return set()
    return {c.get("name") for c in inspector.get_columns(table_name) if c.get("name")}


def _add_column_if_missing(table_name: str, column_name: str, column_ddl: str) -> None:
    inspector = inspect(db.engine)
    if table_name not in inspector.get_table_names():
        return
    existing = _table_columns(table_name)
    if column_name in existing:
        return
    db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_ddl}"))


def ensure_schema_columns() -> None:
    """Best-effort schema guard for existing databases when migrations were skipped."""
    is_sqlite = db.engine.url.drivername.startswith("sqlite")

    _add_column_if_missing("diseases", "image_filename", "image_filename VARCHAR(200)")
    if is_sqlite:
        _add_column_if_missing(
            "diseases",
            "symptom_checklist_json",
            "symptom_checklist_json TEXT DEFAULT '[]'",
        )
    else:
        _add_column_if_missing("diseases", "symptom_checklist_json", "symptom_checklist_json TEXT")

    if "symptom_checklist_json" in _table_columns("diseases"):
        db.session.execute(
            text(
                """
                UPDATE diseases
                SET symptom_checklist_json = '[]'
                WHERE symptom_checklist_json IS NULL OR symptom_checklist_json = ''
                """
            )
        )
    _add_column_if_missing("diseases", "created_by_id", "created_by_id INTEGER")
    _add_column_if_missing("diseases", "updated_by_id", "updated_by_id INTEGER")
    _add_column_if_missing("diseases", "created_at", "created_at DATETIME")
    _add_column_if_missing("diseases", "updated_at", "updated_at DATETIME")
    _add_column_if_missing("diseases", "name_km", "name_km VARCHAR(120)")
    _add_column_if_missing("diseases", "symptoms_km", "symptoms_km TEXT")
    _add_column_if_missing("diseases", "cause_km", "cause_km TEXT")
    _add_column_if_missing("diseases", "treatment_km", "treatment_km TEXT")
    _add_column_if_missing("diseases", "prevention_km", "prevention_km TEXT")

    _add_column_if_missing("feedback", "symptom_check_id", "symptom_check_id INTEGER")
    _add_column_if_missing("feedback", "photo_filename", "photo_filename VARCHAR(220)")

    _add_column_if_missing("symptom_catalog", "created_by_id", "created_by_id INTEGER")
    _add_column_if_missing("symptom_catalog", "updated_by_id", "updated_by_id INTEGER")
    _add_column_if_missing("symptom_catalog", "created_at", "created_at DATETIME")
    _add_column_if_missing("symptom_catalog", "updated_at", "updated_at DATETIME")
    _add_column_if_missing("symptom_catalog", "label_km", "label_km VARCHAR(255)")

    if "label_km" in _table_columns("symptom_catalog"):
        db.session.execute(
            text(
                """
                UPDATE symptom_catalog
                SET label_km = label
                WHERE label_km IS NULL OR label_km = ''
                """
            )
        )

    db.session.commit()
