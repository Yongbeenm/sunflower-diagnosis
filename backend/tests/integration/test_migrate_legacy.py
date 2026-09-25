"""Integration tests for the legacy SQLite data migration pipeline.

Validates:
- Cross-disease symptom deduplication
- Bilingual EN / KM translation splitting and fallback
- Pathogen type inference (fungal, bacterial, viral)
- Unreferenced symptom catalog reporting
- Idempotency (running migration twice produces identical state without duplicate rows)
- Dry-run mode (produces 0 database side-effects)
- Legacy Werkzeug scrypt password authentication and transparent rehash to Argon2id
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import Role, User
from app.models.diagnosis import DiagnosisResult, DiagnosisSession
from app.models.disease import Disease, DiseaseSymptom
from app.models.enums import PathogenType
from app.models.feedback import Feedback
from app.models.ruleset import Ruleset
from app.models.symptom import Symptom, SymptomCategory
from app.models.translation import Translation
from scripts.migrate_legacy import LegacyMigrator

FIXTURE_DB_PATH = "/tmp/sunflower_legacy_sample.db"
TEMP_REVIEW_CSV = "/tmp/test_weights_to_review.csv"


@pytest.fixture(autouse=True)
def _create_legacy_fixture() -> None:
    """Create the small legacy SQLite database required by migration tests."""
    password_salt = "legacy-test-salt"
    password_digest = hashlib.scrypt(
        b"secretPassword123",
        salt=password_salt.encode(),
        n=32768,
        r=8,
        p=1,
        maxmem=128 * 1024 * 1024,
    ).hex()
    password_hash = f"scrypt:32768:8:1${password_salt}${password_digest}"

    connection = sqlite3.connect(FIXTURE_DB_PATH)
    try:
        connection.executescript(
            """
            DROP TABLE IF EXISTS feedback;
            DROP TABLE IF EXISTS symptom_check_results;
            DROP TABLE IF EXISTS symptom_check_symptoms;
            DROP TABLE IF EXISTS symptom_checks;
            DROP TABLE IF EXISTS symptom_catalog;
            DROP TABLE IF EXISTS diseases;
            DROP TABLE IF EXISTS users;

            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT
            );

            CREATE TABLE diseases (
                id INTEGER PRIMARY KEY,
                slug TEXT NOT NULL,
                name TEXT NOT NULL,
                symptoms TEXT,
                cause TEXT,
                treatment TEXT,
                prevention TEXT,
                image_filename TEXT,
                name_km TEXT,
                symptoms_km TEXT,
                cause_km TEXT,
                treatment_km TEXT,
                prevention_km TEXT,
                symptom_checklist_json TEXT,
                created_at TEXT
            );

            CREATE TABLE symptom_catalog (
                id INTEGER PRIMARY KEY,
                label TEXT NOT NULL,
                category TEXT,
                label_km TEXT
            );

            CREATE TABLE symptom_checks (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                created_at TEXT,
                selected_count INTEGER,
                top_disease_slug TEXT,
                top_disease_name TEXT,
                top_score REAL,
                top_percent REAL
            );

            CREATE TABLE symptom_check_symptoms (
                check_id INTEGER,
                symptom_label TEXT
            );

            CREATE TABLE symptom_check_results (
                check_id INTEGER,
                rank INTEGER,
                disease_key TEXT,
                disease_name TEXT,
                score REAL,
                percent REAL,
                matched_json TEXT
            );

            CREATE TABLE feedback (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                subject TEXT,
                message TEXT,
                status TEXT,
                created_at TEXT,
                symptom_check_id INTEGER,
                photo_filename TEXT
            );
            """
        )

        connection.executemany(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
            [
                (1, "grower1", "grower1@example.com", password_hash, "user", "2026-01-01T00:00:00"),
                (2, "expert1", "expert1@example.com", password_hash, "doctor", "2026-01-01T00:00:00"),
                (3, "legacy_admin", "legacy-admin@example.com", password_hash, "admin", "2026-01-01T00:00:00"),
            ],
        )

        checklist = lambda items: json.dumps(items, ensure_ascii=False)
        connection.executemany(
            "INSERT INTO diseases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    1,
                    "downy-mildew",
                    "Downy Mildew",
                    "Wilting or drooping; Yellowing leaves",
                    "Plasmopara halstedii",
                    "Apply fungicide",
                    "Use resistant varieties",
                    None,
                    "ជំងឺរោគផ្សិតទន់",
                    "ស្លឹកក្រៀម; ស្លឹកលឿង",
                    "Plasmopara halstedii",
                    "បាញ់ថ្នាំសម្លាប់ផ្សិត",
                    "ប្រើពូជធន់នឹងជំងឺ",
                    checklist(
                        [
                            {"label": "Wilting or drooping", "category": "leaf", "label_km": "ស្លឹកក្រៀម"},
                            {"label": "Yellowing leaves", "category": "leaf", "label_km": "ស្លឹកលឿង"},
                        ]
                    ),
                    "2026-01-01T00:00:00",
                ),
                (
                    2,
                    "bacterial-blight",
                    "Bacterial Blight",
                    "Wilting or drooping; Stem lesions",
                    "Bacteria",
                    "Remove affected plants",
                    "Improve sanitation",
                    None,
                    "ជំងឺបាក់តេរី",
                    "ស្លឹកក្រៀម; ដំបៅដើម",
                    "បាក់តេរី",
                    "ដករុក្ខជាតិដែលឆ្លង",
                    "រក្សាអនាម័យ",
                    checklist(
                        [
                            {"label": "Wilting or drooping", "category": "leaf", "label_km": "ស្លឹកក្រៀម"},
                            {"label": "Stem lesions", "category": "stem", "label_km": "ដំបៅដើម"},
                        ]
                    ),
                    "2026-01-01T00:00:00",
                ),
                (
                    3,
                    "mosaic-virus",
                    "Mosaic Virus",
                    "Mottled leaves",
                    "Virus",
                    "Remove infected plants",
                    "Control vectors",
                    None,
                    "ជំងឺវីរុសម៉ូសាអ៊ីក",
                    "ស្លឹកមានស្នាម",
                    "វីរុស",
                    "ដករុក្ខជាតិឆ្លង",
                    "គ្រប់គ្រងសត្វល្អិត",
                    checklist(
                        [{"label": "Mottled leaves", "category": "leaf", "label_km": "ស្លឹកមានស្នាម"}]
                    ),
                    "2026-01-01T00:00:00",
                ),
            ],
        )
        connection.execute(
            "INSERT INTO symptom_catalog VALUES (?, ?, ?, ?)",
            (1, "Unreferenced root decay", "root", "រលួយឫស"),
        )
        connection.execute(
            "INSERT INTO symptom_checks VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (1, 1, "2026-01-02T00:00:00", 2, "downy-mildew", "Downy Mildew", 0.8, 80.0),
        )
        connection.executemany(
            "INSERT INTO symptom_check_symptoms VALUES (?, ?)",
            [(1, "Wilting or drooping"), (1, "Yellowing leaves")],
        )
        connection.execute(
            "INSERT INTO symptom_check_results VALUES (?, ?, ?, ?, ?, ?, ?)",
            (1, 1, "downy-mildew", "Downy Mildew", 0.8, 80.0, '["Wilting or drooping"]'),
        )
        connection.execute(
            "INSERT INTO feedback VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (1, 1, "Downy mildew question", "How can I treat it?", "open", "2026-01-02T00:00:00", 1, None),
        )
        connection.commit()
    finally:
        connection.close()


async def ensure_prerequisites(session: AsyncSession) -> None:
    """Ensure roles and categories exist in test DB before migration."""
    roles = [
        ("grower", "Sunflower grower"),
        ("agronomist", "Sunflower agronomist"),
        ("admin", "System administrator"),
    ]
    for r_name, r_desc in roles:
        stmt = select(Role).where(Role.name == r_name)
        if not (await session.execute(stmt)).scalar_one_or_none():
            session.add(Role(name=r_name, description=r_desc))

    categories = [
        ("leaf", 1),
        ("leaf_head", 2),
        ("whole_plant", 3),
        ("stem", 4),
        ("head", 5),
        ("root", 6),
        ("seedling", 7),
        ("environment", 8),
    ]
    for c_code, c_sort in categories:
        c_stmt = select(SymptomCategory).where(SymptomCategory.code == c_code)
        if not (await session.execute(c_stmt)).scalar_one_or_none():
            session.add(SymptomCategory(code=c_code, sort_order=c_sort))

    await session.flush()


@pytest.mark.asyncio
async def test_migration_dry_run_produces_no_db_changes(db_session: AsyncSession) -> None:
    """--dry-run should analyze legacy DB and report counts without committing rows."""
    await ensure_prerequisites(db_session)

    migrator = LegacyMigrator(
        session=db_session,
        db_path=FIXTURE_DB_PATH,
        i18n_en_path=None,
        i18n_km_path=None,
        images_dir="/tmp",
        review_csv=TEMP_REVIEW_CSV,
        dry_run=True,
    )
    report = await migrator.run()

    assert report.dry_run is True
    # Verify DB has 0 migrated diseases
    disease_count = await db_session.scalar(select(func.count(Disease.id)))
    assert disease_count == 0

    # Verify report detected entities
    assert report.stats["diseases"].read == 3
    assert report.stats["users"].read == 3


@pytest.mark.asyncio
async def test_migration_symptom_deduplication_and_associations(db_session: AsyncSession) -> None:
    """Symptoms shared between diseases are deduplicated into ONE row and linked with weights."""
    await ensure_prerequisites(db_session)

    migrator = LegacyMigrator(
        session=db_session,
        db_path=FIXTURE_DB_PATH,
        i18n_en_path=None,
        i18n_km_path=None,
        images_dir="/tmp",
        review_csv=TEMP_REVIEW_CSV,
        dry_run=False,
    )
    report = await migrator.run()

    # Both downy-mildew and bacterial-blight in fixture have "Wilting or drooping"
    wilting_stmt = select(Symptom).where(Symptom.code == "wilting_or_drooping")
    wilting_syms = (await db_session.execute(wilting_stmt)).scalars().all()
    assert len(wilting_syms) == 1, "Wilting or drooping must be deduplicated to exactly 1 Symptom"

    wilting_sym = wilting_syms[0]
    # Check associations in disease_symptoms
    ds_stmt = select(DiseaseSymptom).where(DiseaseSymptom.symptom_id == wilting_sym.id)
    associations = (await db_session.execute(ds_stmt)).scalars().all()
    assert len(associations) == 2, "Wilting or drooping should link to both diseases"
    for ds in associations:
        assert ds.weight == pytest.approx(0.50)
        assert ds.is_required is False
        assert ds.is_pathognomonic is False

    # Check unreferenced catalog reporting
    assert "Unreferenced root decay" in report.unreferenced_catalog

    # Check review CSV was written
    assert Path(TEMP_REVIEW_CSV).is_file()  # noqa: ASYNC240


@pytest.mark.asyncio
async def test_migration_translation_split_and_pathogen_inference(db_session: AsyncSession) -> None:
    """Diseases have translations split into EN/KM and pathogen types correctly inferred."""
    await ensure_prerequisites(db_session)

    migrator = LegacyMigrator(
        session=db_session,
        db_path=FIXTURE_DB_PATH,
        i18n_en_path=None,
        i18n_km_path=None,
        images_dir="/tmp",
        review_csv=TEMP_REVIEW_CSV,
        dry_run=False,
    )
    await migrator.run()

    # Verify downy-mildew
    dm_stmt = select(Disease).where(Disease.slug == "downy-mildew")
    dm = (await db_session.execute(dm_stmt)).scalar_one()
    assert dm.pathogen_type == PathogenType.FUNGAL

    # Verify bacterial-blight
    bb_stmt = select(Disease).where(Disease.slug == "bacterial-blight")
    bb = (await db_session.execute(bb_stmt)).scalar_one()
    assert bb.pathogen_type == PathogenType.BACTERIAL

    # Verify mosaic-virus
    mv_stmt = select(Disease).where(Disease.slug == "mosaic-virus")
    mv = (await db_session.execute(mv_stmt)).scalar_one()
    assert mv.pathogen_type == PathogenType.VIRAL

    # Verify translations for downy-mildew
    t_en_stmt = select(Translation).where(
        (Translation.entity_type == "disease")
        & (Translation.entity_id == dm.id)
        & (Translation.locale == "en")
    )
    t_en = {t.field: t.value for t in (await db_session.execute(t_en_stmt)).scalars().all()}
    assert t_en["name"] == "Downy Mildew"
    assert t_en["cause"] == "Plasmopara halstedii"

    t_km_stmt = select(Translation).where(
        (Translation.entity_type == "disease")
        & (Translation.entity_id == dm.id)
        & (Translation.locale == "km")
    )
    t_km = {t.field: t.value for t in (await db_session.execute(t_km_stmt)).scalars().all()}
    assert t_km["name"] == "ជំងឺរោគផ្សិតទន់"
    assert t_km["treatment"] == "បាញ់ថ្នាំសម្លាប់ផ្សិត"


@pytest.mark.asyncio
async def test_migration_idempotency(db_session: AsyncSession) -> None:
    """Running migration a second time should not duplicate records."""
    await ensure_prerequisites(db_session)

    migrator = LegacyMigrator(
        session=db_session,
        db_path=FIXTURE_DB_PATH,
        i18n_en_path=None,
        i18n_km_path=None,
        images_dir="/tmp",
        review_csv=TEMP_REVIEW_CSV,
        dry_run=False,
    )

    # First run
    await migrator.run()
    d_count_1 = await db_session.scalar(select(func.count(Disease.id)))
    s_count_1 = await db_session.scalar(select(func.count(Symptom.id)))
    u_count_1 = await db_session.scalar(select(func.count(User.id)))

    # Second run
    report_2 = await migrator.run()
    d_count_2 = await db_session.scalar(select(func.count(Disease.id)))
    s_count_2 = await db_session.scalar(select(func.count(Symptom.id)))
    u_count_2 = await db_session.scalar(select(func.count(User.id)))

    assert d_count_1 == d_count_2 == 3
    assert s_count_1 == s_count_2 == 5  # 4 unique from diseases + 1 unreferenced catalog
    assert u_count_1 == u_count_2 == 3
    assert report_2.stats["diseases"].created == 0


@pytest.mark.asyncio
async def test_migration_checks_and_feedback(db_session: AsyncSession) -> None:
    """Historical symptom checks and feedback rows are migrated and linked to inactive ruleset."""
    await ensure_prerequisites(db_session)

    migrator = LegacyMigrator(
        session=db_session,
        db_path=FIXTURE_DB_PATH,
        i18n_en_path=None,
        i18n_km_path=None,
        images_dir="/tmp",
        review_csv=TEMP_REVIEW_CSV,
        dry_run=False,
    )
    await migrator.run()

    # Verify inactive ruleset
    ruleset_stmt = select(Ruleset).where(Ruleset.version == "legacy-import")
    ruleset = (await db_session.execute(ruleset_stmt)).scalar_one()
    assert ruleset.is_active is False

    # Verify diagnosis session
    sessions = (await db_session.execute(select(DiagnosisSession))).scalars().all()
    assert len(sessions) == 1
    session = sessions[0]
    assert session.ruleset_id == ruleset.id
    assert session.symptom_count == 2

    # Verify results
    res_stmt = select(DiagnosisResult).where(DiagnosisResult.session_id == session.id)
    results = (await db_session.execute(res_stmt)).scalars().all()
    assert len(results) == 1
    assert results[0].disease_name_snapshot == "Downy Mildew"
    assert results[0].rank == 1

    # Verify feedback
    feedbacks = (await db_session.execute(select(Feedback))).scalars().all()
    assert len(feedbacks) == 1
    assert feedbacks[0].subject == "Downy mildew question"
    assert feedbacks[0].diagnosis_session_id == session.id


@pytest.mark.asyncio
async def test_migrated_user_authenticates_and_rehashes(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Migrated legacy user logs in with scrypt password and gets rehashed to Argon2id."""
    await ensure_prerequisites(db_session)

    migrator = LegacyMigrator(
        session=db_session,
        db_path=FIXTURE_DB_PATH,
        i18n_en_path=None,
        i18n_km_path=None,
        images_dir="/tmp",
        review_csv=TEMP_REVIEW_CSV,
        dry_run=False,
    )
    await migrator.run()

    # User grower1 has legacy scrypt password 'secretPassword123'
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "grower1@example.com", "password": "secretPassword123"},
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

    # Verify user's hash was upgraded to Argon2id
    u_stmt = select(User).where(User.email == "grower1@example.com")
    user = (await db_session.execute(u_stmt)).scalar_one()
    assert user.password_hash.startswith("$argon2")
