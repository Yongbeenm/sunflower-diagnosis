"""Symptom and symptom category repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.disease import Disease, DiseaseSymptom
from app.models.symptom import Symptom, SymptomCategory
from app.models.translation import Translation


class SymptomRepository:
    """Database operations for symptoms, symptom categories, and translations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_categories(self) -> list[SymptomCategory]:
        """Fetch all symptom categories sorted by sort_order."""
        stmt = select(SymptomCategory).order_by(SymptomCategory.sort_order, SymptomCategory.code)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_category_by_id(self, category_id: int) -> SymptomCategory | None:
        """Fetch category by id."""
        stmt = select(SymptomCategory).where(SymptomCategory.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_category_translations(self, locale: str = "en") -> dict[int, str]:
        """Fetch localized labels for symptom categories."""
        stmt = select(Translation).where(
            Translation.entity_type == "category",
            Translation.field == "label",
            Translation.locale.in_([locale, "en"]),
        )
        result = await self.session.execute(stmt)
        translations = result.scalars().all()

        labels: dict[int, str] = {}
        for t in translations:
            if t.locale == "en":
                labels[t.entity_id] = t.value
        for t in translations:
            if t.locale == locale:
                labels[t.entity_id] = t.value
        return labels

    async def list_symptoms(
        self,
        category_code: str | None = None,
    ) -> list[Symptom]:
        """Fetch all symptoms with loaded categories, optionally filtered by category code."""
        stmt = (
            select(Symptom)
            .join(Symptom.category)
            .options(selectinload(Symptom.category))
            .order_by(SymptomCategory.sort_order, Symptom.code)
        )
        if category_code:
            stmt = stmt.where(SymptomCategory.code == category_code)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_symptom_translations(self, locale: str = "en") -> dict[int, str]:
        """Fetch localized labels for symptoms with English fallback."""
        stmt = select(Translation).where(
            Translation.entity_type == "symptom",
            Translation.field == "label",
            Translation.locale.in_([locale, "en"]),
        )
        result = await self.session.execute(stmt)
        translations = result.scalars().all()

        labels: dict[int, str] = {}
        for t in translations:
            if t.locale == "en":
                labels[t.entity_id] = t.value
        for t in translations:
            if t.locale == locale:
                labels[t.entity_id] = t.value
        return labels

    async def get_symptom_all_translations(self, symptom_id: int) -> dict[str, str]:
        """Fetch all locale labels for a specific symptom."""
        stmt = select(Translation).where(
            Translation.entity_type == "symptom",
            Translation.entity_id == symptom_id,
            Translation.field == "label",
        )
        result = await self.session.execute(stmt)
        return {t.locale: t.value for t in result.scalars().all()}

    async def get_by_id(self, symptom_id: int) -> Symptom | None:
        """Fetch symptom by id with category loaded."""
        stmt = (
            select(Symptom).where(Symptom.id == symptom_id).options(selectinload(Symptom.category))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Symptom | None:
        """Fetch symptom by unique code."""
        stmt = select(Symptom).where(Symptom.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, symptom: Symptom) -> Symptom:
        """Add and flush a symptom."""
        self.session.add(symptom)
        await self.session.flush()
        return symptom

    async def set_translation(
        self,
        symptom_id: int,
        locale: str,
        value: str,
    ) -> None:
        """Upsert symptom label translation."""
        stmt = select(Translation).where(
            Translation.entity_type == "symptom",
            Translation.entity_id == symptom_id,
            Translation.locale == locale,
            Translation.field == "label",
        )
        result = await self.session.execute(stmt)
        trans = result.scalar_one_or_none()
        if trans:
            trans.value = value
        else:
            self.session.add(
                Translation(
                    entity_type="symptom",
                    entity_id=symptom_id,
                    locale=locale,
                    field="label",
                    value=value,
                )
            )
        await self.session.flush()

    async def get_referencing_diseases(self, symptom_id: int) -> list[str]:
        """Find disease slugs or names referencing this symptom in disease_symptoms."""
        stmt = (
            select(Disease.slug)
            .join(DiseaseSymptom, Disease.id == DiseaseSymptom.disease_id)
            .where(DiseaseSymptom.symptom_id == symptom_id)
            .order_by(Disease.slug)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, symptom: Symptom) -> None:
        """Delete symptom and its translations."""
        # Remove translations
        stmt = select(Translation).where(
            Translation.entity_type == "symptom",
            Translation.entity_id == symptom.id,
        )
        translations = (await self.session.execute(stmt)).scalars().all()
        for t in translations:
            await self.session.delete(t)

        await self.session.delete(symptom)
        await self.session.flush()
