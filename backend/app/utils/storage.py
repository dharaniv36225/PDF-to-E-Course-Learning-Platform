"""File storage abstraction: local filesystem or Supabase Storage."""
from __future__ import annotations

import os
import uuid
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    """Persist uploaded files to local disk or Supabase Storage."""

    def __init__(self) -> None:
        self.use_supabase = settings.USE_SUPABASE_STORAGE and bool(settings.SUPABASE_URL)
        if not self.use_supabase:
            Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    def save(self, data: bytes, original_filename: str, user_id: str) -> tuple[str, str]:
        """Save file bytes. Returns (storage_path, provider)."""
        safe_name = f"{uuid.uuid4().hex}_{Path(original_filename).name}"
        key = f"{user_id}/{safe_name}"
        if self.use_supabase:
            return self._save_supabase(data, key), "supabase"
        return self._save_local(data, safe_name), "local"

    def _save_local(self, data: bytes, filename: str) -> str:
        path = os.path.join(settings.UPLOAD_DIR, filename)
        with open(path, "wb") as fh:
            fh.write(data)
        return path

    def _save_supabase(self, data: bytes, key: str) -> str:
        from supabase import create_client

        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
            key, data, {"content-type": "application/pdf", "upsert": "true"}
        )
        return key

    def delete(self, storage_path: str, provider: str) -> None:
        try:
            if provider == "local":
                if os.path.exists(storage_path):
                    os.remove(storage_path)
            elif provider == "supabase":
                from supabase import create_client

                client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
                client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).remove([storage_path])
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to delete file %s: %s", storage_path, exc)


_storage: StorageService | None = None


def get_storage() -> StorageService:
    global _storage
    if _storage is None:
        _storage = StorageService()
    return _storage
