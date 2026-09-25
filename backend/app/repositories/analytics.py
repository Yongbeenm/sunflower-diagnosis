"""Analytics repository executing aggregate queries over diagnosis sessions and feedback."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnosis import DiagnosisSelectedSymptom, DiagnosisSession
from app.models.enums import DiagnosisAnswer, DiagnosisOutcome, FeedbackStatus
from app.models.feedback import Feedback
from app.models.symptom import Symptom
from app.models.translation import Translation


class AnalyticsRepository:
    """Repository for dashboard summary and aggregate metrics."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_total_checks(self) -> int:
        """Count total diagnosis sessions."""
        stmt = select(func.count(DiagnosisSession.id))
        result = await self.session.scalar(stmt)
        return result or 0

    async def get_checks_today(self) -> int:
        """Count diagnosis sessions started today."""
        now = datetime.now(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        stmt = select(func.count(DiagnosisSession.id)).where(
            DiagnosisSession.created_at >= today_start
        )
        result = await self.session.scalar(stmt)
        return result or 0

    async def get_checks_trend_30d(self) -> list[dict[str, Any]]:
        """Return daily counts of diagnosis sessions for the past 30 days."""
        cutoff = datetime.now(UTC) - timedelta(days=30)
        # func.date(created_at) works cleanly across SQLite and Postgres
        date_expr = func.date(DiagnosisSession.created_at)
        stmt = (
            select(date_expr.label("dt"), func.count(DiagnosisSession.id).label("cnt"))
            .where(DiagnosisSession.created_at >= cutoff)
            .group_by(date_expr)
            .order_by(date_expr.asc())
        )
        res = await self.session.execute(stmt)
        rows = res.all()
        return [{"date": str(r.dt), "count": int(r.cnt)} for r in rows]

    async def get_top_symptoms(self, limit: int = 10, locale: str = "en") -> list[dict[str, Any]]:
        """Find most frequently reported positive ('yes') symptoms."""
        stmt = (
            select(
                DiagnosisSelectedSymptom.symptom_id,
                Symptom.code,
                func.count().label("cnt"),
            )
            .join(Symptom, Symptom.id == DiagnosisSelectedSymptom.symptom_id)
            .where(DiagnosisSelectedSymptom.answer == DiagnosisAnswer.YES)
            .group_by(DiagnosisSelectedSymptom.symptom_id, Symptom.code)
            .order_by(func.count().desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        rows = res.all()

        if not rows:
            return []

        symptom_ids = [r.symptom_id for r in rows]

        # Fetch label translations
        t_stmt = select(Translation.entity_id, Translation.value).where(
            Translation.entity_type == "symptom",
            Translation.entity_id.in_(symptom_ids),
            Translation.field == "label",
            Translation.locale.in_([locale, "en"]),
        )
        t_res = await self.session.execute(t_stmt)
        labels = {r.entity_id: r.value for r in t_res.all()}

        output = []
        for r in rows:
            output.append(
                {
                    "symptom_id": r.symptom_id,
                    "code": r.code,
                    "label": labels.get(r.symptom_id, r.code),
                    "count": int(r.cnt),
                }
            )
        return output

    async def get_no_match_patterns(self, limit: int = 5) -> list[dict[str, Any]]:
        """Identify common symptom combinations resulting in no_match outcomes."""
        stmt = (
            select(
                DiagnosisSelectedSymptom.session_id,
                Symptom.code,
            )
            .join(DiagnosisSession, DiagnosisSession.id == DiagnosisSelectedSymptom.session_id)
            .join(Symptom, Symptom.id == DiagnosisSelectedSymptom.symptom_id)
            .where(
                DiagnosisSession.outcome == DiagnosisOutcome.NO_MATCH,
                DiagnosisSelectedSymptom.answer == DiagnosisAnswer.YES,
            )
            .order_by(DiagnosisSelectedSymptom.session_id)
        )
        res = await self.session.execute(stmt)
        rows = res.all()

        # Group codes by session
        session_symptoms: dict[str, list[str]] = {}
        for r in rows:
            sid = str(r.session_id)
            if sid not in session_symptoms:
                session_symptoms[sid] = []
            session_symptoms[sid].append(r.code)

        pattern_counter: Counter[tuple[str, ...]] = Counter()
        for syms in session_symptoms.values():
            if syms:
                pattern_counter[tuple(sorted(syms))] += 1

        top_patterns = pattern_counter.most_common(limit)
        return [{"symptoms": list(pattern), "count": count} for pattern, count in top_patterns]

    async def get_pending_feedback_count(self) -> int:
        """Count unresolved feedback reports."""
        stmt = select(func.count(Feedback.id)).where(
            Feedback.status.in_([FeedbackStatus.OPEN, FeedbackStatus.IN_REVIEW])
        )
        result = await self.session.scalar(stmt)
        return result or 0
