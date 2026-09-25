"""Media service handling magic-byte validation, EXIF stripping, and thumbnail generation."""

from __future__ import annotations

import io
import uuid
from typing import ClassVar

from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import ValidationFailedError
from app.models.auth import User
from app.repositories.media import MediaRepository
from app.schemas.content import MediaResponse
from app.services.media.storage import LocalDiskBackend, MediaBackend, S3MediaBackend


class MediaService:
    """Processes uploaded images, enforces magic-byte constraints, and delegates storage."""

    # Magic byte signatures
    PNG_SIGNATURE: ClassVar[bytes] = b"\x89PNG\r\n\x1a\n"
    JPEG_SIGNATURE: ClassVar[bytes] = b"\xff\xd8\xff"
    RIFF_HEADER: ClassVar[bytes] = b"RIFF"
    WEBP_SIGNATURE: ClassVar[bytes] = b"WEBP"

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = MediaRepository(session)
        self.settings = get_settings()
        self.backend: MediaBackend = self._get_storage_backend()

    def _get_storage_backend(self) -> MediaBackend:
        if self.settings.MEDIA_BACKEND == "s3":
            return S3MediaBackend(
                bucket_name="sunflower-media",
                region="ap-southeast-1",
                public_cdn_url=self.settings.MEDIA_PUBLIC_URL,
            )
        return LocalDiskBackend(
            root_dir=self.settings.MEDIA_ROOT,
            public_base_url=self.settings.MEDIA_PUBLIC_URL,
        )

    def _detect_mime_and_format(self, data: bytes) -> tuple[str, str, str]:
        """Detect MIME type, file extension, and PIL format from magic bytes.

        Raises:
            ValidationFailedError: if magic bytes do not match png, jpeg, or webp.
        """
        if len(data) < 12:
            raise ValidationFailedError(
                detail="File content too short to determine format",
                errors=[{"field": "file", "message": "File is empty or corrupted"}],
            )

        if data.startswith(self.PNG_SIGNATURE):
            return "image/png", "png", "PNG"

        if data.startswith(self.JPEG_SIGNATURE):
            return "image/jpeg", "jpg", "JPEG"

        if data.startswith(self.RIFF_HEADER) and data[8:12] == self.WEBP_SIGNATURE:
            return "image/webp", "webp", "WEBP"

        raise ValidationFailedError(
            detail="Unsupported or fraudulent image format",
            errors=[
                {
                    "field": "file",
                    "message": "File magic bytes do not match allowed formats (PNG, JPEG, WebP).",
                }
            ],
        )

    async def upload(
        self,
        raw_bytes: bytes,
        filename: str | None,
        user: User | None,
    ) -> MediaResponse:
        """Validate, strip EXIF, generate thumbnail, persist to disk/object storage,
        and record DB entity.
        """
        if len(raw_bytes) > self.settings.MEDIA_MAX_BYTES:
            max_bytes = self.settings.MEDIA_MAX_BYTES
            raise ValidationFailedError(
                detail=f"File exceeds maximum allowed size of {max_bytes} bytes",
                errors=[{"field": "file", "message": "File size exceeds 5MB limit"}],
            )

        mime_type, ext, pil_format = self._detect_mime_and_format(raw_bytes)

        try:
            image = Image.open(io.BytesIO(raw_bytes))
            image.load()
        except Exception as exc:
            raise ValidationFailedError(
                detail="Corrupted or unreadable image payload",
                errors=[{"field": "file", "message": "Image decoder failed"}],
            ) from exc

        width, height = image.size

        # Strip EXIF by recreating clean image data
        clean_buf = io.BytesIO()
        # Convert RGBA to RGB for JPEG if necessary
        clean_img: Image.Image = image
        if pil_format == "JPEG" and image.mode in ("RGBA", "P"):
            clean_img = image.convert("RGB")

        # Save without any EXIF dictionary
        clean_img.save(clean_buf, format=pil_format)
        clean_bytes = clean_buf.getvalue()

        # Generate thumbnail (max 300x300, keeping aspect ratio)
        thumb_img = clean_img.copy()
        thumb_img.thumbnail((300, 300))
        thumb_buf = io.BytesIO()
        thumb_img.save(thumb_buf, format=pil_format)
        thumb_bytes = thumb_buf.getvalue()

        # Build unique storage keys
        unique_id = uuid.uuid4().hex
        main_key = f"{unique_id}.{ext}"
        thumb_key = f"{unique_id}_thumb.{ext}"

        # Store files
        main_url = await self.backend.save(main_key, clean_bytes, mime_type)
        await self.backend.save(thumb_key, thumb_bytes, mime_type)

        # Database record
        media = await self.repository.create(
            storage_key=main_key,
            mime_type=mime_type,
            bytes_count=len(clean_bytes),
            width=width,
            height=height,
            uploaded_by_id=user.id if user else None,
        )

        return MediaResponse(
            id=media.id,
            url=main_url,
            width=media.width,
            height=media.height,
        )
