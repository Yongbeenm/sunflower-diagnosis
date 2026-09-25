"""Diagnosis repository handling database access for rulesets, diseases, and sessions."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.diagnosis import DiagnosisResult, DiagnosisSelectedSymptom, DiagnosisSession
from app.models.disease import Disease, DiseaseSymptom
from app.models.ruleset import Ruleset
from app.models.symptom import Symptom
from app.models.translation import Translation


class DiagnosisRepository:
    """Async database operations for the expert system diagnosis engine."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_active_ruleset(self) -> Ruleset | None:
        """Fetch the currently active ruleset."""
        stmt = select(Ruleset).where(Ruleset.is_active.is_(True))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_published_diseases_with_rules(self) -> Sequence[Disease]:
        """Fetch all published diseases and their symptom weights in ONE query via selectinload."""
        stmt = (
            select(Disease)
            .where(Disease.is_published.is_(True))
            .options(
                selectinload(Disease.disease_symptoms).selectinload(DiseaseSymptom.symptom),
            )
            .order_by(Disease.slug)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_disease_names(self, locale: str = "en") -> dict[int, str]:
        """Fetch localized disease names with fallback to English."""
        stmt = select(Translation).where(
            Translation.entity_type == "disease",
            Translation.field == "name",
            Translation.locale.in_([locale, "en"]),
        )
        result = await self.session.execute(stmt)
        translations = result.scalars().all()

        names: dict[int, str] = {}
        # First populate English fallback
        for t in translations:
            if t.locale == "en":
                names[t.entity_id] = t.value
        # Override with requested locale
        for t in translations:
            if t.locale == locale:
                names[t.entity_id] = t.value

        return names

    async def get_symptom_code_map(self) -> dict[int, str]:
        """Fetch mapping from symptom_id to symptom code."""
        stmt = select(Symptom.id, Symptom.code)
        result = await self.session.execute(stmt)
        return dict(result.tuples().all())

    async def save_session(self, session: DiagnosisSession) -> DiagnosisSession:
        """Add session and cascade children to the database session and flush."""
        self.session.add(session)
        await self.session.flush()
        return session

    async def get_session_by_id(self, session_id: uuid.UUID) -> DiagnosisSession | None:
        """Fetch diagnosis session with all relationships eager-loaded."""
        stmt = (
            select(DiagnosisSession)
            .where(DiagnosisSession.id == session_id)
            .options(
                selectinload(DiagnosisSession.ruleset),
                selectinload(DiagnosisSession.top_disease),
                selectinload(DiagnosisSession.results).selectinload(DiagnosisResult.disease),
                selectinload(DiagnosisSession.selected_symptoms).selectinload(
                    DiagnosisSelectedSymptom.symptom
                ),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_sessions(
        self,
        user_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[DiagnosisSession], int]:
        """Fetch paginated diagnosis session history for a user, sorted descending by creation."""
        count_stmt = (
            select(func.count())
            .select_from(DiagnosisSession)
            .where(DiagnosisSession.user_id == user_id)
        )
        count_res = await self.session.execute(count_stmt)
        total = count_res.scalar_one()

        stmt = (
            select(DiagnosisSession)
            .where(DiagnosisSession.user_id == user_id)
            .options(selectinload(DiagnosisSession.top_disease))
            .order_by(DiagnosisSession.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        return items, total
