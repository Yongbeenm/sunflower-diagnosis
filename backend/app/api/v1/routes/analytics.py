"""Analytics API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_permission
from app.schemas.analytics import AnalyticsOverviewResponse
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Dashboard analytics overview (checks, trends, top symptoms, no-match patterns)",
    dependencies=[Depends(require_permission("analytics:read"))],
)
async def get_analytics_overview(
    db: Annotated[AsyncSession, Depends(get_db)],
    accept_language: Annotated[str | None, Header()] = None,
) -> AnalyticsOverviewResponse:
    """Get aggregated analytics data for the admin/agronomist dashboard."""
    locale = "km" if accept_language and "km" in accept_language.lower() else "en"
    service = AnalyticsService(db)
    return await service.get_overview(locale=locale)
