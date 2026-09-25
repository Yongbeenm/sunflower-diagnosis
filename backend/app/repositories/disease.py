"""Disease repository with full-text search, filtering, and bulk weights."""

from __future__ import annotations

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.disease import Disease, DiseaseSymptom
from app.models.enums import PathogenType
from app.models.symptom import Symptom, SymptomCategory
from app.models.translation import Translation


class DiseaseRepository:
    """Database operations for Disease entities, symptom weights, and multilingual translations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, disease_id: int) -> Disease | None:
        """Fetch disease by ID with image media loaded."""
        stmt = (
            select(Disease)
            .where(Disease.id == disease_id)
            .options(selectinload(Disease.image_media))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Disease | None:
        """Fetch disease by slug with image and full symptom graph loaded."""
        stmt = (
            select(Disease)
            .where(Disease.slug == slug)
            .options(
                selectinload(Disease.image_media),
                selectinload(Disease.disease_symptoms)
                .selectinload(DiseaseSymptom.symptom)
                .selectinload(Symptom.category),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug_simple(self, slug: str) -> Disease | None:
        """Fetch disease by slug without relationships."""
        stmt = select(Disease).where(Disease.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_diseases(
        self,
        q: str | None = None,
        category: str | None = None,
        pathogen: PathogenType | None = None,
        published: bool | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Disease], int]:
        """Query diseases with full-text search, faceted filters, and pagination."""
        stmt = select(Disease).options(selectinload(Disease.image_media))
        count_stmt = select(func.count(distinct(Disease.id)))

        # Published filter
        if published is not None:
            stmt = stmt.where(Disease.is_published == published)
            count_stmt = count_stmt.where(Disease.is_published == published)

        # Pathogen type filter
        if pathogen is not None:
            stmt = stmt.where(Disease.pathogen_type == pathogen)
            count_stmt = count_stmt.where(Disease.pathogen_type == pathogen)

        # Category filter (diseases with at least one symptom in category)
        if category:
            cat_subquery = (
                select(DiseaseSymptom.disease_id)
                .join(Symptom, DiseaseSymptom.symptom_id == Symptom.id)
                .join(SymptomCategory, Symptom.category_id == SymptomCategory.id)
                .where(
                    (SymptomCategory.code == category) | (SymptomCategory.id.cast(str) == category)
                )
            )
            stmt = stmt.where(Disease.id.in_(cat_subquery))
            count_stmt = count_stmt.where(Disease.id.in_(cat_subquery))

        # Full-text search
        if q and q.strip():
            query_term = q.strip()
            bind = self.session.bind
            is_postgres = bind is not None and bind.dialect.name == "postgresql"

            if is_postgres:
                # Use PostgreSQL tsvector match
                search_filter = Disease.search_vector.op("@@")(
                    func.plainto_tsquery("simple", query_term)
                ) | Disease.slug.ilike(f"%{query_term}%")
            else:
                # Portable fallback for SQLite in-memory test suite
                trans_subquery = select(Translation.entity_id).where(
                    Translation.entity_type == "disease",
                    Translation.field.in_(["name", "description"]),
                    Translation.value.ilike(f"%{query_term}%"),
                )
                search_filter = Disease.slug.ilike(f"%{query_term}%") | Disease.id.in_(
                    trans_subquery
                )

            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = stmt.order_by(Disease.slug).offset((page - 1) * size).limit(size)
        items_res = await self.session.execute(stmt)
        items = list(items_res.scalars().all())

        return items, total

    async def get_translations_for_diseases(
        self,
        disease_ids: list[int],
        locale: str = "en",
    ) -> dict[int, dict[str, str]]:
        """Fetch field translations for a set of diseases with English fallback."""
        if not disease_ids:
            return {}

        stmt = select(Translation).where(
            Translation.entity_type == "disease",
            Translation.entity_id.in_(disease_ids),
            Translation.locale.in_([locale, "en"]),
        )
        result = await self.session.execute(stmt)
        translations = result.scalars().all()

        data: dict[int, dict[str, str]] = {did: {} for did in disease_ids}
        # Populate English fallback first
        for t in translations:
            if t.locale == "en":
                data[t.entity_id][t.field] = t.value
        # Override with requested locale
        for t in translations:
            if t.locale == locale:
                data[t.entity_id][t.field] = t.value

        return data

    async def get_all_disease_translations(self, disease_id: int) -> dict[str, dict[str, str]]:
        """Fetch all translations for a disease mapped as {locale: {field: value}}."""
        stmt = select(Translation).where(
            Translation.entity_type == "disease",
            Translation.entity_id == disease_id,
        )
        result = await self.session.execute(stmt)
        all_trans: dict[str, dict[str, str]] = {}
        for t in result.scalars().all():
            all_trans.setdefault(t.locale, {})[t.field] = t.value
        return all_trans

    async def create(self, disease: Disease) -> Disease:
        """Add and flush disease."""
        self.session.add(disease)
        await self.session.flush()
        return disease

    async def set_translation(
        self,
        disease_id: int,
        locale: str,
        field: str,
        value: str,
    ) -> None:
        """Upsert a translation field."""
        stmt = select(Translation).where(
            Translation.entity_type == "disease",
            Translation.entity_id == disease_id,
            Translation.locale == locale,
            Translation.field == field,
        )
        result = await self.session.execute(stmt)
        trans = result.scalar_one_or_none()
        if trans:
            trans.value = value
        else:
            self.session.add(
                Translation(
                    entity_type="disease",
                    entity_id=disease_id,
                    locale=locale,
                    field=field,
                    value=value,
                )
            )
        await self.session.flush()

    async def get_symptom_ids(self, symptom_ids: list[int]) -> set[int]:
        """Return subset of symptom IDs that actually exist in the database."""
        if not symptom_ids:
            return set()
        stmt = select(Symptom.id).where(Symptom.id.in_(symptom_ids))
        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    async def bulk_replace_symptoms(
        self,
        disease_id: int,
        symptom_weights: list[tuple[int, float, bool, bool]],
    ) -> None:
        """Atomically delete existing symptom associations and insert new ones."""
        # 1. Delete all existing disease_symptoms for this disease
        del_stmt = select(DiseaseSymptom).where(DiseaseSymptom.disease_id == disease_id)
        existing = (await self.session.execute(del_stmt)).scalars().all()
        for item in existing:
            await self.session.delete(item)

        await self.session.flush()

        # 2. Insert new associations
        for sym_id, weight, is_req, is_patho in symptom_weights:
            ds = DiseaseSymptom(
                disease_id=disease_id,
                symptom_id=sym_id,
                weight=weight,
                is_required=is_req,
                is_pathognomonic=is_patho,
            )
            self.session.add(ds)

        await self.session.flush()
