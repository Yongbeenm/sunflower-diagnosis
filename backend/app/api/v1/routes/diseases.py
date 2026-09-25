"""Disease management and catalog API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_permission
from app.models.auth import User
from app.models.enums import PathogenType
from app.schemas.content import (
    DiseaseCreateRequest,
    DiseaseDetailResponse,
    DiseaseListResponse,
    DiseaseSymptomsBulkUpdateRequest,
    DiseaseTranslationsUpdateRequest,
    DiseaseUpdateRequest,
)
from app.services.disease import DiseaseService

router = APIRouter(prefix="/diseases", tags=["diseases"])


@router.get(
    "",
    response_model=DiseaseListResponse,
    summary="List and search diseases",
)
async def list_diseases(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: Annotated[str | None, Query(description="Full-text search keyword")] = None,
    category: Annotated[str | None, Query(description="Symptom category code or ID")] = None,
    pathogen: Annotated[PathogenType | None, Query(description="Pathogen classification")] = None,
    published: Annotated[bool | None, Query(description="Publication status filter")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
    locale: Annotated[str, Query(description="Content locale")] = "en",
) -> DiseaseListResponse:
    """Search and filter disease candidates with full-text search and pagination."""
    service = DiseaseService(db)
    return await service.list_diseases(
        q=q,
        category=category,
        pathogen=pathogen,
        published=published,
        page=page,
        size=size,
        locale=locale,
    )


@router.get(
    "/{slug}",
    response_model=DiseaseDetailResponse,
    summary="Get disease details by slug",
)
async def get_disease(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    locale: Annotated[str, Query(description="Content locale")] = "en",
) -> DiseaseDetailResponse:
    """Retrieve full disease details with grouped symptoms, image URL, and English fallback."""
    service = DiseaseService(db)
    return await service.get_disease(slug=slug, locale=locale)


@router.post(
    "",
    response_model=DiseaseDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create disease",
)
async def create_disease(
    req: DiseaseCreateRequest,
    current_user: Annotated[User, Depends(require_permission("disease:create"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DiseaseDetailResponse:
    """Create a new sunflower disease or disorder candidate."""
    service = DiseaseService(db)
    return await service.create_disease(req=req, user=current_user)


@router.patch(
    "/{id}",
    response_model=DiseaseDetailResponse,
    summary="Update disease attributes",
)
async def update_disease(
    id: int,
    req: DiseaseUpdateRequest,
    current_user: Annotated[User, Depends(require_permission("disease:update"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DiseaseDetailResponse:
    """Update disease attributes (pathogen classification, image, publication status)."""
    service = DiseaseService(db)
    return await service.update_disease(disease_id=id, req=req, user=current_user)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Permanently delete disease",
)
async def delete_disease(
    id: int,
    current_user: Annotated[User, Depends(require_permission("disease:delete"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Permanently delete a disease from the database."""
    service = DiseaseService(db)
    await service.delete_disease(disease_id=id, user=current_user)


@router.put(
    "/{id}/symptoms",
    response_model=DiseaseDetailResponse,
    summary="Bulk replace disease symptom weights",
)
async def bulk_replace_disease_symptoms(
    id: int,
    req: DiseaseSymptomsBulkUpdateRequest,
    current_user: Annotated[User, Depends(require_permission("disease:update"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DiseaseDetailResponse:
    """Atomically replace the full set of symptom weights for a disease in one transaction.

    Validates that all symptom IDs exist. Returns 422 with exact invalid index if any ID is unknown.
    """
    service = DiseaseService(db)
    return await service.replace_symptoms(disease_id=id, req=req, user=current_user)


@router.put(
    "/{id}/translations/{locale}",
    response_model=DiseaseDetailResponse,
    summary="Bulk update disease translations for locale",
)
async def update_disease_translations(
    id: int,
    locale: str,
    req: DiseaseTranslationsUpdateRequest,
    current_user: Annotated[User, Depends(require_permission("disease:update"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DiseaseDetailResponse:
    """Update or insert localized fields for a disease."""
    service = DiseaseService(db)
    return await service.update_translations(
        disease_id=id,
        locale=locale,
        req=req,
        user=current_user,
    )
