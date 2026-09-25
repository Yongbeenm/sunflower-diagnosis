"""Media repository for storing asset metadata."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import Media


class MediaRepository:
    """Database persistence for Media metadata records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        storage_key: str,
        mime_type: str,
        bytes_count: int,
        width: int | None,
        height: int | None,
        uploaded_by_id: int | None,
    ) -> Media:
        """Create and flush a new media record."""
        media = Media(
            storage_key=storage_key,
            mime_type=mime_type,
            bytes=bytes_count,
            width=width,
            height=height,
            uploaded_by_id=uploaded_by_id,
        )
        self.session.add(media)
        await self.session.flush()
        return media

    async def get_by_id(self, media_id: int) -> Media | None:
        """Fetch media record by primary key."""
        stmt = select(Media).where(Media.id == media_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_key(self, storage_key: str) -> Media | None:
        """Fetch media record by unique storage key."""
        stmt = select(Media).where(Media.storage_key == storage_key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
