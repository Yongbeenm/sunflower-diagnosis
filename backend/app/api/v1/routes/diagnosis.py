"""Diagnosis API routes for running evaluations, previews, and viewing history."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, require_permission
from app.models.auth import User
from app.repositories.diagnosis import DiagnosisRepository
from app.schemas.diagnosis import (
    DiagnosisRequest,
    DiagnosisResponse,
    DiagnosisSessionDetailResponse,
    DiagnosisSessionListResponse,
)
from app.services.engine.runner import DiagnosisRunner

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])


@router.post(
    "/sessions",
    response_model=DiagnosisResponse,
    summary="Run diagnosis and persist session",
)
async def create_diagnosis_session(
    req: DiagnosisRequest,
    current_user: Annotated[User, Depends(require_permission("diagnosis:run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DiagnosisResponse:
    """Evaluate observed symptoms against active rules, record session and evidence.

    Returns ranked candidate disease results.
    """
    repo = DiagnosisRepository(db)
    runner = DiagnosisRunner(repo)
    return await runner.create_session(req, current_user)


@router.post(
    "/preview",
    response_model=DiagnosisResponse,
    summary="Stateless diagnosis preview",
)
async def preview_diagnosis(
    req: DiagnosisRequest,
    current_user: Annotated[User, Depends(require_permission("diagnosis:run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DiagnosisResponse:
    """Evaluate observed symptoms without persisting session or result rows."""
    repo = DiagnosisRepository(db)
    runner = DiagnosisRunner(repo)
    return await runner.preview(req)


@router.get(
    "/sessions",
    response_model=DiagnosisSessionListResponse,
    summary="List own diagnosis history",
)
async def list_my_diagnosis_sessions(
    current_user: Annotated[User, Depends(require_permission("diagnosis:read_own"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> DiagnosisSessionListResponse:
    """Retrieve paginated list of current user's past diagnosis sessions."""
    repo = DiagnosisRepository(db)
    runner = DiagnosisRunner(repo)
    return await runner.get_history(user_id=current_user.id, page=page, size=size)


@router.get(
    "/sessions/{id}",
    response_model=DiagnosisSessionDetailResponse,
    summary="Get diagnosis session detail",
)
async def get_diagnosis_session(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DiagnosisSessionDetailResponse:
    """Retrieve full details of a diagnosis session.

    Accessible by session owner, or users with 'diagnosis:read_all' permission.
    Returns 404 for unowned sessions if caller lacks read_all.
    """
    repo = DiagnosisRepository(db)
    runner = DiagnosisRunner(repo)
    return await runner.get_session(session_id=id, current_user=current_user)
