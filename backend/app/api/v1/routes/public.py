"""Public API routes (no authentication required)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.models.disease import Disease
from app.models.symptom import Symptom

router = APIRouter(prefix="/public", tags=["public"])


class SystemStatsResponse(BaseModel):
    """Public system statistics."""

    total_diseases: int
    total_symptoms: int
    published_diseases: int


@router.get(
    "/stats",
    response_model=SystemStatsResponse,
    summary="Get public system statistics",
)
async def get_system_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SystemStatsResponse:
    """Get real-time counts of diseases and symptoms in the system.
    
    This endpoint is public and does not require authentication.
    Used for the homepage statistics display.
    """
    # Count total diseases
    disease_count_result = await db.execute(select(func.count(Disease.id)))
    total_diseases = disease_count_result.scalar() or 0

    # Count published diseases
    published_count_result = await db.execute(
        select(func.count(Disease.id)).where(Disease.is_published == True)  # noqa: E712
    )
    published_diseases = published_count_result.scalar() or 0

    # Count total symptoms
    symptom_count_result = await db.execute(select(func.count(Symptom.id)))
    total_symptoms = symptom_count_result.scalar() or 0

    return SystemStatsResponse(
        total_diseases=total_diseases,
        total_symptoms=total_symptoms,
        published_diseases=published_diseases,
    )
