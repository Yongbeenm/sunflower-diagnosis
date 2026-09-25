"""Analytics service computing dashboard metrics for agronomists and administrators."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.analytics import AnalyticsRepository
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    DailyChecksTrend,
    NoMatchPattern,
    TopSymptom,
)


class AnalyticsService:
    """Coordinates dashboard metric calculations."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = AnalyticsRepository(session)

    async def get_overview(self, locale: str = "en") -> AnalyticsOverviewResponse:
        """Fetch consolidated metrics for dashboard."""
        total = await self.repo.get_total_checks()
        today = await self.repo.get_checks_today()
        trend_rows = await self.repo.get_checks_trend_30d()
        symptom_rows = await self.repo.get_top_symptoms(limit=10, locale=locale)
        no_match_rows = await self.repo.get_no_match_patterns(limit=5)
        pending_feedback = await self.repo.get_pending_feedback_count()

        return AnalyticsOverviewResponse(
            checks_today=today,
            checks_total=total,
            checks_trend_30d=[DailyChecksTrend(**t) for t in trend_rows],
            top_symptoms=[TopSymptom(**s) for s in symptom_rows],
            no_match_patterns=[NoMatchPattern(**p) for p in no_match_rows],
            pending_feedback_count=pending_feedback,
        )
