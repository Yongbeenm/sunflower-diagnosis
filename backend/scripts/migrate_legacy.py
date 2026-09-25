"""Legacy SQLite to Sunflower Expert System PostgreSQL migration script.

Migrates:
- Users (preserves Werkzeug scrypt/pbkdf2 password_hash, maps roles:
  user->grower, doctor->agronomist, admin->admin)
- Inactive ruleset 'legacy-import' (algorithm='legacy_ratio_v0', is_active=False)
- Media assets (validates dimensions with PIL, strips EXIF, generates thumbnails)
- Diseases + Translations (EN and KM split, pathogen_type inference with audit logging)
- Symptoms (deduplication across diseases, canonical category mapping, keyify code generation)
- Disease-Symptom associations (initial 0.50 weights, is_required=False, is_pathognomonic=False)
- Symptom Catalog merge (unreferenced catalog items reported)
- Historical diagnosis sessions, answers ('yes'), results, and snapshots
- Feedback with status mapping and optional photo linking
- Exports weights_to_review.csv for agronomist tuning
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import csv
import io
import json
import os
import re
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

# Load .env if present before settings are instantiated
for env_candidate in [Path(".env"), Path("../.env")]:
    if env_candidate.exists():
        with open(env_candidate) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

import structlog
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import async_session_factory
from app.models.auth import Role, User
from app.models.diagnosis import (
    DiagnosisResult,
    DiagnosisSelectedSymptom,
    DiagnosisSession,
)
from app.models.disease import Disease, DiseaseSymptom
from app.models.enums import (
    DiagnosisAnswer,
    DiagnosisOutcome,
    FeedbackStatus,
    PathogenType,
)
from app.models.feedback import Feedback
from app.models.media import Media
from app.models.ruleset import Ruleset
from app.models.symptom import Symptom, SymptomCategory
from app.models.translation import Translation
from app.services.media.storage import LocalDiskBackend, MediaBackend, S3MediaBackend

logger = structlog.get_logger(__name__)

LEGACY_RULESET_VERSION = "legacy-import"
LEGACY_RULESET_ALGORITHM = "legacy_ratio_v0"

_CATEGORY_CANONICAL_MAP: dict[str, str] = {
    "leaf": "leaf",
    "leafhead": "leaf_head",
    "leaf_head": "leaf_head",
    "wholeplant": "whole_plant",
    "whole_plant": "whole_plant",
    "stem": "stem",
    "head": "head",
    "headflower": "head",
    "head_flower": "head",
    "root": "root",
    "seed": "seedling",
    "seedling": "seedling",
    "seedseedling": "seedling",
    "seed_seedling": "seedling",
    "environment": "environment",
    "env": "environment",
    "environmental": "environment",
    "general": "whole_plant",
}

ROLE_MAP: dict[str, str] = {
    "user": "grower",
    "doctor": "agronomist",
    "admin": "admin",
}

STATUS_MAP: dict[str, FeedbackStatus] = {
    "open": FeedbackStatus.OPEN,
    "in_review": FeedbackStatus.IN_REVIEW,
    "resolved": FeedbackStatus.RESOLVED,
}


def normalize_symptom_label(label: str) -> str:
    """Normalize whitespace and lower-case for cross-disease deduplication."""
    return re.sub(r"\s+", " ", (label or "").strip().lower())


def keyify(label: str) -> str:
    """Generate a clean URL/identifier code from a symptom label."""
    v = (label or "").strip().lower()
    v = re.sub(r"[^a-z0-9]+", "_", v)
    v = re.sub(r"_{2,}", "_", v).strip("_")
    return (v or "symptom")[:64]


def canonical_category_code(raw_category: str | None) -> str:
    """Map legacy free-text categories into one of 8 canonical category codes."""
    if not raw_category:
        return "whole_plant"
    cleaned = re.sub(r"[^a-z0-9]+", "", raw_category.strip().lower())
    return _CATEGORY_CANONICAL_MAP.get(cleaned, "whole_plant")


def infer_pathogen_type(slug: str, name: str, cause: str = "") -> tuple[PathogenType, str]:
    """Infer pathogen type from slug and name per AGENTS.md / PROMPTS.md rule:
    (bacterial-* → bacterial; *-virus, mosaic, yellows → viral; otherwise fungal).
    """
    slug_l = slug.lower().strip()
    name_l = name.lower().strip()

    # 1. bacterial-* / crown-gall -> bacterial
    if slug_l.startswith("bacterial") or name_l.startswith("bacterial") or slug_l == "crown-gall":
        return PathogenType.BACTERIAL, "Matched bacterial-* pattern or crown-gall"

    # 2. *-virus, mosaic, yellows -> viral
    if (
        slug_l.endswith("virus")
        or "-virus" in slug_l
        or "virus" in name_l
        or "mosaic" in slug_l
        or "mosaic" in name_l
        or "yellows" in slug_l
        or "yellows" in name_l
    ):
        return PathogenType.VIRAL, "Matched *-virus, mosaic, or yellows pattern"

    # 3. Otherwise fungal
    return PathogenType.FUNGAL, "Default fungal classification"


@dataclass
class EntityStats:
    read: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0


@dataclass
class MigrationReport:
    dry_run: bool = False
    stats: dict[str, EntityStats] = field(default_factory=dict)
    pathogen_inferences: list[dict[str, str]] = field(default_factory=list)
    unreferenced_catalog: list[str] = field(default_factory=list)
    missing_media_files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def get_stat(self, name: str) -> EntityStats:
        if name not in self.stats:
            self.stats[name] = EntityStats()
        return self.stats[name]


class LegacyMigrator:
    """Performs the full migration from legacy SQLite files into PostgreSQL."""

    def __init__(
        self,
        session: AsyncSession,
        db_path: str,
        i18n_en_path: str | None,
        i18n_km_path: str | None,
        images_dir: str,
        review_csv: str = "weights_to_review.csv",
        dry_run: bool = False,
    ) -> None:
        self.session = session
        self.db_path = db_path
        self.i18n_en_path = i18n_en_path
        self.i18n_km_path = i18n_km_path
        self.images_dir = Path(images_dir)
        self.review_csv = Path(review_csv)
        self.dry_run = dry_run
        self.report = MigrationReport(dry_run=dry_run)
        self.settings = get_settings()
        self.media_backend: MediaBackend = self._init_media_backend()

    def _init_media_backend(self) -> MediaBackend:
        if self.settings.MEDIA_BACKEND == "s3":
            return S3MediaBackend(
                bucket_name="sunflower-media",
                region="ap-southeast-1",
                public_cdn_url=self.settings.MEDIA_PUBLIC_URL,
            )
        return LocalDiskBackend(
            root_dir=self.settings.MEDIA_ROOT,
            public_base_url=self.settings.MEDIA_PUBLIC_URL,
        )

    def _load_i18n_map(self, path: str | None) -> dict[str, str]:
        """Load legacy i18n messages database into a key->text dict."""
        if not path or not os.path.exists(path):
            return {}
        result: dict[str, str] = {}
        try:
            con = sqlite3.connect(path)
            cur = con.cursor()
            cur.execute("SELECT msg_key, msg_text FROM i18n_messages")
            for k, text in cur.fetchall():
                if k and text:
                    result[k.strip()] = text.strip()
            con.close()
        except Exception as exc:
            self.report.warnings.append(f"Failed to read i18n db {path}: {exc}")
        return result

    async def run(self) -> MigrationReport:
        """Execute migration pipeline in atomic stages."""
        self.report = MigrationReport(dry_run=self.dry_run)
        logger.info("migration.start", db=self.db_path, dry_run=self.dry_run)

        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Legacy database file not found: {self.db_path}")

        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row

        km_translations = self._load_i18n_map(self.i18n_km_path)

        try:
            # 0. Ensure schema exists if running in SQLite / standalone environment
            from sqlalchemy.ext.asyncio import AsyncEngine

            bind = self.session.bind
            if isinstance(bind, AsyncEngine) and "sqlite" in str(bind.url):
                import app.models  # noqa: F401
                from app.db.base import Base

                async with bind.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)

            # 1. Ruleset
            ruleset = await self._migrate_ruleset()

            # 2. Roles mapping cache
            role_cache = await self._get_roles()

            # 3. Category mapping cache
            category_cache = await self._get_categories()

            # 4. Users
            user_map = await self._migrate_users(con, role_cache)

            # 5. Media
            media_map = await self._migrate_media(con)

            # 6. Diseases & Translations
            disease_map = await self._migrate_diseases(con, media_map)

            # 7. Symptoms & Catalog
            symptom_map = await self._migrate_symptoms_and_catalog(
                con, category_cache, km_translations
            )

            # 8. Disease-Symptoms associations & CSV Export
            await self._migrate_disease_symptoms(con, disease_map, symptom_map)

            # 9. Symptom checks (Diagnosis sessions & results)
            await self._migrate_checks(con, ruleset, user_map, disease_map, symptom_map)

            # 10. Feedback
            await self._migrate_feedback(con, user_map, media_map)

            if not self.dry_run:
                await self.session.commit()
                logger.info("migration.committed")
            else:
                await self.session.rollback()
                logger.info("migration.dry_run_complete")

        except Exception as exc:
            await self.session.rollback()
            logger.error("migration.failed", error=str(exc))
            raise
        finally:
            con.close()

        return self.report

    async def _migrate_ruleset(self) -> Ruleset:
        """Ensure inactive 'legacy-import' ruleset exists."""
        stats = self.report.get_stat("rulesets")
        stats.read += 1
        stmt = select(Ruleset).where(Ruleset.version == LEGACY_RULESET_VERSION)
        result = await self.session.execute(stmt)
        ruleset = result.scalar_one_or_none()

        if not ruleset:
            ruleset = Ruleset(
                version=LEGACY_RULESET_VERSION,
                algorithm=LEGACY_RULESET_ALGORITHM,
                params={
                    "legacy": True,
                    "description": "Legacy monolith scoring ratio (matched / total)",
                },
                is_active=False,
            )
            if not self.dry_run:
                self.session.add(ruleset)
                await self.session.flush()
            stats.created += 1
        else:
            stats.skipped += 1

        return ruleset

    async def _get_roles(self) -> dict[str, Role]:
        stmt = select(Role)
        res = await self.session.execute(stmt)
        roles = {r.name: r for r in res.scalars().all()}
        if not roles:
            default_roles = [
                ("grower", "Sunflower grower seeking disease diagnoses and management guidance"),
                ("agronomist", "Agricultural expert maintaining diseases and symptom weights"),
                ("admin", "System administrator with full operational access"),
            ]
            for rname, rdesc in default_roles:
                r = Role(name=rname, description=rdesc)
                self.session.add(r)
                roles[rname] = r
            if not self.dry_run:
                await self.session.flush()
        return roles

    async def _get_categories(self) -> dict[str, SymptomCategory]:
        stmt = select(SymptomCategory)
        res = await self.session.execute(stmt)
        categories = {c.code: c for c in res.scalars().all()}
        if not categories:
            default_categories = [
                ("leaf", 1),
                ("leaf_head", 2),
                ("whole_plant", 3),
                ("stem", 4),
                ("head", 5),
                ("root", 6),
                ("seedling", 7),
                ("environment", 8),
            ]
            for ccode, csort in default_categories:
                cat = SymptomCategory(code=ccode, sort_order=csort)
                self.session.add(cat)
                categories[ccode] = cat
            if not self.dry_run:
                await self.session.flush()
        return categories

    async def _migrate_users(
        self, con: sqlite3.Connection, role_cache: dict[str, Role]
    ) -> dict[int, User]:
        """Migrate users preserving Werkzeug password hashes and mapping roles."""
        stats = self.report.get_stat("users")
        user_map: dict[int, User] = {}
        cur = con.cursor()
        cur.execute("SELECT id, username, email, password_hash, role, created_at FROM users")
        rows = cur.fetchall()

        for row in rows:
            stats.read += 1
            legacy_id = row["id"]
            email = (row["email"] or "").strip().lower()
            username = (row["username"] or "").strip()
            legacy_role = (row["role"] or "user").strip().lower()
            target_role_name = ROLE_MAP.get(legacy_role, "grower")
            role = role_cache.get(target_role_name)

            if not role:
                self.report.warnings.append(
                    f"User {email}: role '{target_role_name}' not found in DB."
                )
                stats.skipped += 1
                continue

            # Look up existing user by email or username
            stmt = select(User).where((User.email == email) | (User.username == username))
            existing_res = await self.session.execute(stmt)
            user = existing_res.scalar_one_or_none()

            created_at_val = datetime.now(UTC)
            if row["created_at"]:
                with contextlib.suppress(Exception):
                    created_at_val = datetime.fromisoformat(row["created_at"]).replace(tzinfo=UTC)

            if not user:
                user = User(
                    email=email,
                    username=username,
                    password_hash=row["password_hash"],
                    role_id=role.id,
                    is_active=True,
                    created_at=created_at_val,
                )
                if not self.dry_run:
                    self.session.add(user)
                    await self.session.flush()
                stats.created += 1
            else:
                # Update role and password_hash if not matching
                user.role_id = role.id
                if not user.password_hash.startswith("$argon2"):
                    user.password_hash = row["password_hash"]
                stats.updated += 1

            user_map[legacy_id] = user

        return user_map

    async def _migrate_media(self, con: sqlite3.Connection) -> dict[str, Media]:
        """Process legacy image files into media table and file store."""
        stats = self.report.get_stat("media")
        media_map: dict[str, Media] = {}
        cur = con.cursor()
        cur.execute("SELECT DISTINCT image_filename FROM diseases WHERE image_filename IS NOT NULL")
        filenames = [r[0] for r in cur.fetchall() if r[0]]

        for filename in filenames:
            stats.read += 1
            img_path = self.images_dir / filename
            if not img_path.exists():
                self.report.missing_media_files.append(str(img_path))
                stats.skipped += 1
                continue

            storage_key = f"legacy_{filename}"
            # Check existing media
            stmt = select(Media).where(Media.storage_key == storage_key)
            res = await self.session.execute(stmt)
            existing_media = res.scalar_one_or_none()

            if existing_media:
                media_map[filename] = existing_media
                stats.skipped += 1
                continue

            try:
                raw_bytes = img_path.read_bytes()
                image = Image.open(io.BytesIO(raw_bytes))
                image.load()
                width, height = image.size

                # Format detection
                ext = img_path.suffix.lstrip(".").lower()
                mime_type = f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"
                pil_format = "JPEG" if ext in ("jpg", "jpeg") else "PNG"

                clean_buf = io.BytesIO()
                clean_img: Image.Image = image
                if pil_format == "JPEG" and image.mode in ("RGBA", "P"):
                    clean_img = image.convert("RGB")
                clean_img.save(clean_buf, format=pil_format)
                clean_bytes = clean_buf.getvalue()

                # Thumbnail
                thumb_img = clean_img.copy()
                thumb_img.thumbnail((300, 300))
                thumb_buf = io.BytesIO()
                thumb_img.save(thumb_buf, format=pil_format)
                thumb_bytes = thumb_buf.getvalue()
                thumb_key = f"legacy_thumb_{filename}"

                if not self.dry_run:
                    await self.media_backend.save(storage_key, clean_bytes, mime_type)
                    await self.media_backend.save(thumb_key, thumb_bytes, mime_type)

                    media = Media(
                        storage_key=storage_key,
                        mime_type=mime_type,
                        bytes=len(clean_bytes),
                        width=width,
                        height=height,
                    )
                    self.session.add(media)
                    await self.session.flush()
                    media_map[filename] = media
                else:
                    # Simulated media object for dry-run
                    media = Media(
                        id=len(media_map) + 1,
                        storage_key=storage_key,
                        mime_type=mime_type,
                        bytes=len(clean_bytes),
                        width=width,
                        height=height,
                    )
                    media_map[filename] = media

                stats.created += 1

            except Exception as exc:
                self.report.warnings.append(f"Failed to process image {filename}: {exc}")
                stats.skipped += 1

        return media_map

    async def _migrate_diseases(
        self, con: sqlite3.Connection, media_map: dict[str, Media]
    ) -> dict[str, Disease]:
        """Migrate diseases, infer pathogen types, and split EN/KM translations."""
        stats = self.report.get_stat("diseases")
        trans_stats = self.report.get_stat("translations")
        disease_map: dict[str, Disease] = {}
        cur = con.cursor()
        cur.execute("""
            SELECT id, slug, name, symptoms, cause, treatment, prevention,
                   image_filename, name_km, symptoms_km, cause_km, treatment_km,
                   prevention_km, created_at
            FROM diseases
        """)
        rows = cur.fetchall()

        for row in rows:
            stats.read += 1
            slug = row["slug"].strip()
            name = (row["name"] or "").strip()
            cause = (row["cause"] or "").strip()

            pathogen_type, reason = infer_pathogen_type(slug, name, cause)
            self.report.pathogen_inferences.append(
                {
                    "slug": slug,
                    "name": name,
                    "pathogen_type": pathogen_type.value,
                    "reason": reason,
                }
            )

            img_fn = row["image_filename"]
            media = media_map.get(img_fn) if img_fn else None

            stmt = select(Disease).where(Disease.slug == slug)
            res = await self.session.execute(stmt)
            disease = res.scalar_one_or_none()

            created_at_val = datetime.now(UTC)
            if row["created_at"]:
                with contextlib.suppress(Exception):
                    created_at_val = datetime.fromisoformat(row["created_at"]).replace(tzinfo=UTC)

            if not disease:
                disease = Disease(
                    slug=slug,
                    pathogen_type=pathogen_type,
                    image_media_id=media.id if media else None,
                    is_published=True,
                    created_at=created_at_val,
                )
                if not self.dry_run:
                    self.session.add(disease)
                    await self.session.flush()
                stats.created += 1
            else:
                disease.pathogen_type = pathogen_type
                if media:
                    disease.image_media_id = media.id
                disease.is_published = True
                stats.updated += 1

            disease_map[slug] = disease

            # Write translations
            # EN translations
            en_fields = {
                "name": name,
                "symptoms": (row["symptoms"] or "").strip(),
                "cause": cause,
                "treatment": (row["treatment"] or "").strip(),
                "prevention": (row["prevention"] or "").strip(),
            }
            # KM translations
            km_fields = {
                "name": (row["name_km"] or "").strip(),
                "symptoms": (row["symptoms_km"] or "").strip(),
                "cause": (row["cause_km"] or "").strip(),
                "treatment": (row["treatment_km"] or "").strip(),
                "prevention": (row["prevention_km"] or "").strip(),
            }

            if not self.dry_run:
                for f_name, f_val in en_fields.items():
                    if f_val:
                        await self._upsert_translation(
                            "disease", disease.id, "en", f_name, f_val, trans_stats
                        )

                for f_name, f_val in km_fields.items():
                    en_val = en_fields.get(f_name, "")
                    # Skip when empty or byte-identical to English
                    if f_val and f_val != en_val:
                        await self._upsert_translation(
                            "disease", disease.id, "km", f_name, f_val, trans_stats
                        )

        return disease_map

    async def _upsert_translation(
        self,
        entity_type: str,
        entity_id: int,
        locale: str,
        field: str,
        value: str,
        stats: EntityStats,
    ) -> None:
        stats.read += 1
        stmt = select(Translation).where(
            (Translation.entity_type == entity_type)
            & (Translation.entity_id == entity_id)
            & (Translation.locale == locale)
            & (Translation.field == field)
        )
        res = await self.session.execute(stmt)
        trans = res.scalar_one_or_none()
        if not trans:
            trans = Translation(
                entity_type=entity_type,
                entity_id=entity_id,
                locale=locale,
                field=field,
                value=value,
            )
            self.session.add(trans)
            stats.created += 1
        else:
            if trans.value != value:
                trans.value = value
                stats.updated += 1
            else:
                stats.skipped += 1

    async def _migrate_symptoms_and_catalog(
        self,
        con: sqlite3.Connection,
        category_cache: dict[str, SymptomCategory],
        km_translations: dict[str, str],
    ) -> dict[str, Symptom]:
        """Deduplicate symptoms across checklists, map categories, merge catalog."""
        symptom_stats = self.report.get_stat("symptoms")
        trans_stats = self.report.get_stat("translations")

        # 1. Collect all symptoms from disease checklists
        cur = con.cursor()
        cur.execute("SELECT slug, symptom_checklist_json FROM diseases")

        # Key: normalized_label -> {label_en, label_km, category_code, diseases: []}
        deduped: dict[str, dict[str, Any]] = {}
        for row in cur.fetchall():
            slug = row["slug"]
            raw_json = row["symptom_checklist_json"]
            if not raw_json:
                continue
            items: list[Any] = []
            with contextlib.suppress(Exception):
                items = json.loads(raw_json)

            for item in items:
                if not isinstance(item, dict):
                    continue
                label_en = (item.get("label") or "").strip()
                if not label_en:
                    continue
                norm = normalize_symptom_label(label_en)
                label_km = (item.get("label_km") or "").strip()
                cat_code = canonical_category_code(item.get("category"))

                if norm not in deduped:
                    deduped[norm] = {
                        "label_en": label_en,
                        "label_km": label_km,
                        "category_code": cat_code,
                        "diseases": [slug],
                    }
                else:
                    deduped[norm]["diseases"].append(slug)
                    if not deduped[norm]["label_km"] and label_km:
                        deduped[norm]["label_km"] = label_km

        # 2. Merge symptom_catalog
        cur.execute("SELECT id, label, category, label_km FROM symptom_catalog")
        catalog_rows = cur.fetchall()

        for crow in catalog_rows:
            clabel = (crow["label"] or "").strip()
            if not clabel:
                continue
            norm = normalize_symptom_label(clabel)
            clabel_km = (crow["label_km"] or "").strip()
            ccat_code = canonical_category_code(crow["category"])

            if norm in deduped:
                # Merge km translation if missing
                if not deduped[norm]["label_km"] and clabel_km:
                    deduped[norm]["label_km"] = clabel_km
            else:
                # Catalog item not in any disease checklist
                self.report.unreferenced_catalog.append(clabel)
                deduped[norm] = {
                    "label_en": clabel,
                    "label_km": clabel_km,
                    "category_code": ccat_code,
                    "diseases": [],
                }

        # 3. Insert or update symptoms and their translations
        symptom_map: dict[str, Symptom] = {}
        seen_codes: set[str] = set()

        for norm, sdata in deduped.items():
            symptom_stats.read += 1
            label_en = sdata["label_en"]
            label_km = sdata["label_km"]
            # Fallback to i18n_km translations if available
            if not label_km and label_en in km_translations:
                label_km = km_translations[label_en]

            cat_code = sdata["category_code"]
            category = category_cache.get(cat_code) or category_cache.get("whole_plant")
            if not category:
                self.report.warnings.append(
                    f"Category '{cat_code}' not found for symptom {label_en}"
                )
                continue

            base_code = keyify(label_en)
            code = base_code
            suffix = 1
            while code in seen_codes:
                suffix += 1
                code = f"{base_code}_{suffix}"[:64]
            seen_codes.add(code)

            stmt = select(Symptom).where(Symptom.code == code)
            res = await self.session.execute(stmt)
            symptom = res.scalar_one_or_none()

            is_env = cat_code == "environment"

            if not symptom:
                symptom = Symptom(
                    code=code,
                    category_id=category.id,
                    is_environmental=is_env,
                )
                if not self.dry_run:
                    self.session.add(symptom)
                    await self.session.flush()
                symptom_stats.created += 1
            else:
                symptom.category_id = category.id
                symptom.is_environmental = is_env
                symptom_stats.updated += 1

            if not self.dry_run:
                # Write translations
                await self._upsert_translation(
                    "symptom", symptom.id, "en", "label", label_en, trans_stats
                )
                if label_km and label_km != label_en:
                    await self._upsert_translation(
                        "symptom", symptom.id, "km", "label", label_km, trans_stats
                    )

            symptom_map[norm] = symptom

        return symptom_map

    async def _migrate_disease_symptoms(
        self,
        con: sqlite3.Connection,
        disease_map: dict[str, Disease],
        symptom_map: dict[str, Symptom],
    ) -> None:
        """Create disease_symptoms associations and write weights_to_review.csv."""
        stats = self.report.get_stat("disease_symptoms")
        cur = con.cursor()
        cur.execute("SELECT slug, name, symptom_checklist_json FROM diseases")

        csv_rows: list[dict[str, str]] = []

        for row in cur.fetchall():
            slug = row["slug"]
            disease_name = row["name"] or slug
            raw_json = row["symptom_checklist_json"]
            disease = disease_map.get(slug)
            if not disease or not raw_json:
                continue

            items: list[Any] = []
            with contextlib.suppress(Exception):
                items = json.loads(raw_json)

            for item in items:
                if not isinstance(item, dict):
                    continue
                label_en = (item.get("label") or "").strip()
                if not label_en:
                    continue
                norm = normalize_symptom_label(label_en)
                symptom = symptom_map.get(norm)
                if not symptom:
                    continue

                stats.read += 1
                cat_code = canonical_category_code(item.get("category"))
                label_km = (item.get("label_km") or "").strip()

                stmt = select(DiseaseSymptom).where(
                    (DiseaseSymptom.disease_id == disease.id)
                    & (DiseaseSymptom.symptom_id == symptom.id)
                )
                res = await self.session.execute(stmt)
                ds = res.scalar_one_or_none()

                if not ds:
                    ds = DiseaseSymptom(
                        disease_id=disease.id,
                        symptom_id=symptom.id,
                        weight=Decimal("0.50"),
                        is_required=False,
                        is_pathognomonic=False,
                    )
                    if not self.dry_run:
                        self.session.add(ds)
                    stats.created += 1
                else:
                    stats.skipped += 1

                csv_rows.append(
                    {
                        "disease_slug": slug,
                        "disease_name": disease_name,
                        "category": cat_code,
                        "symptom_code": symptom.code,
                        "symptom_label_en": label_en,
                        "symptom_label_km": label_km,
                        "weight": "0.50",
                        "is_required": "False",
                        "is_pathognomonic": "False",
                    }
                )

        if not self.dry_run:
            await self.session.flush()

        # Write CSV
        with open(self.review_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "disease_slug",
                    "disease_name",
                    "category",
                    "symptom_code",
                    "symptom_label_en",
                    "symptom_label_km",
                    "weight",
                    "is_required",
                    "is_pathognomonic",
                ],
            )
            writer.writeheader()
            writer.writerows(csv_rows)

        logger.info("migration.csv_written", path=str(self.review_csv), rows=len(csv_rows))

    async def _migrate_checks(
        self,
        con: sqlite3.Connection,
        ruleset: Ruleset,
        user_map: dict[int, User],
        disease_map: dict[str, Disease],
        symptom_map: dict[str, Symptom],
    ) -> None:
        """Migrate legacy symptom_checks, selections, and results."""
        session_stats = self.report.get_stat("diagnosis_sessions")
        selection_stats = self.report.get_stat("selected_symptoms")
        result_stats = self.report.get_stat("diagnosis_results")

        cur = con.cursor()
        cur.execute("""
            SELECT id, user_id, created_at, selected_count, top_disease_slug,
                   top_disease_name, top_score, top_percent
            FROM symptom_checks
        """)
        checks = cur.fetchall()

        for chk in checks:
            session_stats.read += 1
            chk_id = chk["id"]
            legacy_uid = chk["user_id"]
            user = user_map.get(legacy_uid)
            top_slug = chk["top_disease_slug"]
            top_disease = disease_map.get(top_slug) if top_slug else None

            created_at_val = datetime.now(UTC)
            if chk["created_at"]:
                with contextlib.suppress(Exception):
                    created_at_val = datetime.fromisoformat(chk["created_at"]).replace(tzinfo=UTC)

            top_conf = None
            if chk["top_percent"] is not None:
                top_conf = Decimal(str(round(chk["top_percent"] / 100, 3)))

            outcome = DiagnosisOutcome.MATCHED if top_disease else DiagnosisOutcome.NO_MATCH

            # Create session with a deterministic UUID or random
            session_uuid = uuid.uuid5(uuid.NAMESPACE_OID, f"legacy_check_{chk_id}")

            stmt = select(DiagnosisSession).where(DiagnosisSession.id == session_uuid)
            existing_sess = (await self.session.execute(stmt)).scalar_one_or_none()

            if not existing_sess:
                session_obj = DiagnosisSession(
                    id=session_uuid,
                    user_id=user.id if user else None,
                    ruleset_id=ruleset.id,
                    locale="en",
                    symptom_count=chk["selected_count"] or 0,
                    top_disease_id=top_disease.id if top_disease else None,
                    top_confidence=top_conf,
                    outcome=outcome,
                    created_at=created_at_val,
                )
                if not self.dry_run:
                    self.session.add(session_obj)
                    await self.session.flush()
                session_stats.created += 1
            else:
                session_obj = existing_sess
                session_stats.skipped += 1

            # Migrate selected symptoms
            cur_s = con.cursor()
            cur_s.execute(
                "SELECT symptom_label FROM symptom_check_symptoms WHERE check_id = ?",
                (chk_id,),
            )
            for srow in cur_s.fetchall():
                selection_stats.read += 1
                slabel = srow["symptom_label"]
                norm = normalize_symptom_label(slabel)
                symptom = symptom_map.get(norm)
                if not symptom:
                    continue

                if not self.dry_run:
                    sel_stmt = select(DiagnosisSelectedSymptom).where(
                        (DiagnosisSelectedSymptom.session_id == session_obj.id)
                        & (DiagnosisSelectedSymptom.symptom_id == symptom.id)
                    )
                    if not (await self.session.execute(sel_stmt)).scalar_one_or_none():
                        sel = DiagnosisSelectedSymptom(
                            session_id=session_obj.id,
                            symptom_id=symptom.id,
                            answer=DiagnosisAnswer.YES,
                        )
                        self.session.add(sel)
                        selection_stats.created += 1
                    else:
                        selection_stats.skipped += 1
                else:
                    selection_stats.created += 1

            # Migrate results
            cur_r = con.cursor()
            cur_r.execute(
                """SELECT rank, disease_key, disease_name, score, percent, matched_json
                   FROM symptom_check_results WHERE check_id = ?""",
                (chk_id,),
            )
            for rrow in cur_r.fetchall():
                result_stats.read += 1
                dkey = rrow["disease_key"]
                res_disease = disease_map.get(dkey)
                score_val = Decimal(str(round(rrow["score"] or 0.0, 3)))
                conf_val = Decimal(str(round((rrow["percent"] or 0) / 100, 3)))
                evidence_dict: dict[str, Any] = {}
                if rrow["matched_json"]:
                    with contextlib.suppress(Exception):
                        evidence_dict = {"matched": json.loads(rrow["matched_json"])}
                    if not evidence_dict:
                        evidence_dict = {"raw": rrow["matched_json"]}

                if not self.dry_run:
                    res_stmt = select(DiagnosisResult).where(
                        (DiagnosisResult.session_id == session_obj.id)
                        & (DiagnosisResult.rank == rrow["rank"])
                    )
                    if not (await self.session.execute(res_stmt)).scalar_one_or_none():
                        dresult = DiagnosisResult(
                            session_id=session_obj.id,
                            rank=rrow["rank"],
                            disease_id=res_disease.id if res_disease else None,
                            disease_name_snapshot=rrow["disease_name"] or dkey,
                            score=score_val,
                            confidence=conf_val,
                            evidence=evidence_dict,
                        )
                        self.session.add(dresult)
                        result_stats.created += 1
                    else:
                        result_stats.skipped += 1
                else:
                    result_stats.created += 1

        if not self.dry_run:
            await self.session.flush()

    async def _migrate_feedback(
        self,
        con: sqlite3.Connection,
        user_map: dict[int, User],
        media_map: dict[str, Media],
    ) -> None:
        """Migrate feedback rows and link photos/sessions."""
        stats = self.report.get_stat("feedback")
        cur = con.cursor()
        cur.execute("""
            SELECT id, user_id, subject, message, status, created_at,
                   symptom_check_id, photo_filename
            FROM feedback
        """)
        rows = cur.fetchall()

        for row in rows:
            stats.read += 1
            user = user_map.get(row["user_id"])
            subject = row["subject"] or "Feedback"
            message = row["message"] or ""
            raw_status = (row["status"] or "open").lower().strip()
            status_val = STATUS_MAP.get(raw_status, FeedbackStatus.OPEN)

            sess_uuid = None
            if row["symptom_check_id"]:
                sess_uuid = uuid.uuid5(
                    uuid.NAMESPACE_OID, f"legacy_check_{row['symptom_check_id']}"
                )

            media = None
            if row["photo_filename"]:
                fn = row["photo_filename"]
                media = media_map.get(fn)
                if not media:
                    self.report.warnings.append(f"Feedback photo file not found: {fn}")

            created_at_val = datetime.now(UTC)
            if row["created_at"]:
                with contextlib.suppress(Exception):
                    created_at_val = datetime.fromisoformat(row["created_at"]).replace(tzinfo=UTC)

            stmt = select(Feedback).where(
                (Feedback.subject == subject)
                & (Feedback.message == message)
                & (Feedback.user_id == (user.id if user else None))
            )
            res = await self.session.execute(stmt)
            fb = res.scalar_one_or_none()

            if not fb:
                fb = Feedback(
                    user_id=user.id if user else None,
                    diagnosis_session_id=sess_uuid,
                    subject=subject,
                    message=message,
                    media_id=media.id if media else None,
                    status=status_val,
                    created_at=created_at_val,
                )
                if not self.dry_run:
                    self.session.add(fb)
                stats.created += 1
            else:
                stats.skipped += 1

        if not self.dry_run:
            await self.session.flush()


def print_migration_report(report: MigrationReport) -> None:
    """Format and print the detailed migration audit report."""
    mode_str = "DRY-RUN (No changes applied)" if report.dry_run else "LIVE MIGRATION"
    print("\n" + "=" * 70)
    print(f" SUNFLOWER EXPERT SYSTEM — DATA MIGRATION REPORT ({mode_str})")
    print("=" * 70 + "\n")

    print("1. ENTITY SUMMARY:")
    print("-" * 60)
    print(f"{'Entity':<25} {'Read':<10} {'Created':<10} {'Updated':<10} {'Skipped':<10}")
    print("-" * 60)
    for entity, stat in report.stats.items():
        print(
            f"{entity:<25} {stat.read:<10} {stat.created:<10} {stat.updated:<10} {stat.skipped:<10}"
        )
    print("-" * 60)

    print("\n2. PATHOGEN TYPE INFERENCES:")
    print("-" * 60)
    for inf in report.pathogen_inferences:
        print(f" • {inf['slug']:<30} -> {inf['pathogen_type']:<10} ({inf['reason']})")

    if report.unreferenced_catalog:
        print(f"\n3. UNREFERENCED SYMPTOM CATALOG ENTRIES ({len(report.unreferenced_catalog)}):")
        print("-" * 60)
        for cat in report.unreferenced_catalog:
            print(f" • {cat}")

    if report.missing_media_files:
        print(f"\n4. MISSING MEDIA FILES ({len(report.missing_media_files)}):")
        print("-" * 60)
        for mf in report.missing_media_files:
            print(f" ⚠️  {mf}")

    if report.warnings:
        print(f"\n5. WARNINGS ({len(report.warnings)}):")
        print("-" * 60)
        for w in report.warnings:
            print(f" ⚠️  {w}")

    print("\n" + "=" * 70)
    print(" IMPORTANT NOTE FOR AGRONOMIST:")
    print(" All migrated disease-symptom association weights have been seeded at 0.50.")
    print(" NO DIAGNOSIS IS TRUSTWORTHY UNTIL WEIGHTS ARE REVIEWED AND TUNED.")
    print(" Review and update weights via the Admin console or weights_to_review.csv.")
    print("=" * 70 + "\n")


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate legacy Sunflower SQLite database to new schema."
    )
    parser.add_argument(
        "--db-path", required=True, help="Path to legacy doctor_sunflower.db SQLite file"
    )
    parser.add_argument(
        "--i18n-en-path", default=None, help="Path to legacy i18n_en.db SQLite file"
    )
    parser.add_argument(
        "--i18n-km-path", default=None, help="Path to legacy i18n_km.db SQLite file"
    )
    parser.add_argument(
        "--images-dir", default="app/static/images", help="Path to legacy image directory"
    )
    parser.add_argument(
        "--review-csv",
        default="weights_to_review.csv",
        help="Path to output weights_to_review.csv",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print migration plan without writing to database",
    )
    args = parser.parse_args()

    async with async_session_factory() as session:
        migrator = LegacyMigrator(
            session=session,
            db_path=args.db_path,
            i18n_en_path=args.i18n_en_path,
            i18n_km_path=args.i18n_km_path,
            images_dir=args.images_dir,
            review_csv=args.review_csv,
            dry_run=args.dry_run,
        )
        report = await migrator.run()
        print_migration_report(report)


if __name__ == "__main__":
    asyncio.run(main())
