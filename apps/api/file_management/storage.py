from __future__ import annotations

from pathlib import Path
import aiofiles
from typing import Any


class LocalStorage:
    """Store files on the local filesystem."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, filename: str, content: bytes) -> str:
        path = self.base_dir / filename
        async with aiofiles.open(path, "wb") as f:
            await f.write(content)
        return str(path)

    def path(self, filename: str) -> Path:
        return self.base_dir / filename


class S3Storage:
    """Stub storage adapter for AWS S3."""

    def __init__(self, settings: Any) -> None:
        self.settings = settings
        # In real implementation configure boto3 client

    async def save(self, filename: str, content: bytes) -> str:
        raise NotImplementedError("S3 storage not implemented")

    def path(self, filename: str) -> Path:
        raise NotImplementedError("S3 storage not implemented")
