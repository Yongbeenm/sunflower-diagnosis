"""Media API route handling image uploads with magic-byte validation."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.auth import User
from app.schemas.content import MediaResponse
from app.services.media.service import MediaService

router = APIRouter(prefix="/media", tags=["media"])


@router.post(
    "",
    response_model=MediaResponse,
    summary="Upload image media (PNG, JPEG, WebP)",
)
async def upload_media(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MediaResponse:
    """Upload an image asset.

    Validates magic bytes, strips EXIF metadata, generates a thumbnail,
    and returns asset metadata with public URL.
    """
    data = await file.read()
    service = MediaService(db)
    return await service.upload(
        raw_bytes=data,
        filename=file.filename,
        user=current_user,
    )
