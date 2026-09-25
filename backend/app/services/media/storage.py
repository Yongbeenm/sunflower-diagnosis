"""Media storage abstraction and backends."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path


class MediaBackend(ABC):
    """Abstract storage backend for uploaded images and thumbnails."""

    @abstractmethod
    async def save(self, storage_key: str, data: bytes, content_type: str) -> str:
        """Persist media bytes and return its public URL."""
        ...

    @abstractmethod
    async def get_url(self, storage_key: str) -> str:
        """Resolve public URL for a given storage key."""
        ...

    @abstractmethod
    async def delete(self, storage_key: str) -> None:
        """Remove media asset from storage."""
        ...


class LocalDiskBackend(MediaBackend):
    """Local filesystem storage implementation."""

    def __init__(self, root_dir: str, public_base_url: str) -> None:
        self.root_path = Path(root_dir)
        self.public_base_url = public_base_url.rstrip("/")
        try:
            self.root_path.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError):
            self.root_path = Path("/tmp/sunflower_media")  # noqa: S108
            self.root_path.mkdir(parents=True, exist_ok=True)

    async def save(self, storage_key: str, data: bytes, content_type: str) -> str:
        """Write file to local disk and return public accessible URL."""
        file_path = self.root_path / storage_key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(data)
        return await self.get_url(storage_key)

    async def get_url(self, storage_key: str) -> str:
        """Build public URL pointing to local serving mount."""
        return f"{self.public_base_url}/{storage_key}"

    async def delete(self, storage_key: str) -> None:
        """Delete local file if it exists."""
        file_path = self.root_path / storage_key
        if file_path.exists():
            os.remove(file_path)


class S3MediaBackend(MediaBackend):
    """Documented seam for AWS S3 / Cloudflare R2 / MinIO storage.

    To activate, configure S3_BUCKET, S3_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
    and install `aioboto3`.
    """

    def __init__(self, bucket_name: str, region: str, public_cdn_url: str) -> None:
        self.bucket_name = bucket_name
        self.region = region
        self.public_cdn_url = public_cdn_url.rstrip("/")

    async def save(self, storage_key: str, data: bytes, content_type: str) -> str:
        raise NotImplementedError("S3 backend requires aioboto3 and AWS credentials configured.")

    async def get_url(self, storage_key: str) -> str:
        return f"{self.public_cdn_url}/{storage_key}"

    async def delete(self, storage_key: str) -> None:
        raise NotImplementedError("S3 backend requires aioboto3 and AWS credentials configured.")
