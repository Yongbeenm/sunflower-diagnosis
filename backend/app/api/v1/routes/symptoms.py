"""Symptom and symptom category API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_permission
from app.models.auth import User
from app.schemas.content import (
    CategoryGroupedSymptoms,
    SymptomCategoryResponse,
    SymptomCreateRequest,
    SymptomDetailResponse,
    SymptomUpdateRequest,
)
from app.services.symptom import SymptomService

router = APIRouter(tags=["symptoms"])


@router.get(
    "/symptom-categories",
    response_model=list[SymptomCategoryResponse],
    summary="List symptom categories",
)
async def list_symptom_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    locale: Annotated[str, Query()] = "en",
) -> list[SymptomCategoryResponse]:
    """Retrieve all plant anatomy and environmental symptom categories."""
    service = SymptomService(db)
    return await service.list_categories(locale=locale)


@router.get(
    "/symptoms",
    response_model=list[CategoryGroupedSymptoms],
    summary="List symptoms grouped by category",
)
async def list_symptoms(
    db: Annotated[AsyncSession, Depends(get_db)],
    category: Annotated[str | None, Query()] = None,
    locale: Annotated[str, Query()] = "en",
) -> list[CategoryGroupedSymptoms]:
    """Retrieve symptoms grouped by category, ordered by sort_order and label.

    Feeds the symptom checker UI.
    """
    service = SymptomService(db)
    return await service.get_grouped_symptoms(category_code=category, locale=locale)


@router.get(
    "/symptoms/{id}",
    response_model=SymptomDetailResponse,
    summary="Get symptom details",
)
async def get_symptom_detail(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    locale: Annotated[str, Query()] = "en",
) -> SymptomDetailResponse:
    """Retrieve full detail and localized labels for a specific symptom."""
    service = SymptomService(db)
    return await service.get_symptom(symptom_id=id, locale=locale)


@router.post(
    "/symptoms",
    response_model=SymptomDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create symptom",
)
async def create_symptom(
    req: SymptomCreateRequest,
    current_user: Annotated[User, Depends(require_permission("symptom:create"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SymptomDetailResponse:
    """Create a new symptom indicator."""
    service = SymptomService(db)
    return await service.create_symptom(req=req, user=current_user)


@router.patch(
    "/symptoms/{id}",
    response_model=SymptomDetailResponse,
    summary="Update symptom",
)
async def update_symptom(
    id: int,
    req: SymptomUpdateRequest,
    current_user: Annotated[User, Depends(require_permission("symptom:update"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SymptomDetailResponse:
    """Update symptom attributes or localized labels."""
    service = SymptomService(db)
    return await service.update_symptom(symptom_id=id, req=req, user=current_user)


@router.delete(
    "/symptoms/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete symptom",
)
async def delete_symptom(
    id: int,
    current_user: Annotated[User, Depends(require_permission("symptom:delete"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a symptom.

    Fails with 409 Conflict if any disease rule currently references this symptom.
    """
    service = SymptomService(db)
    await service.delete_symptom(symptom_id=id, user=current_user)
