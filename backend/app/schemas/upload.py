"""Upload schemas."""
from __future__ import annotations

import uuid
from datetime import datetime

from app.schemas.common import ORMModel


class UploadRead(ORMModel):
    id: uuid.UUID
    filename: str
    original_filename: str
    content_type: str
    size_bytes: int
    page_count: int
    status: str
    storage_provider: str
    error_message: str | None = None
    created_at: datetime


class UploadDetail(UploadRead):
    extracted_text: str | None = None
