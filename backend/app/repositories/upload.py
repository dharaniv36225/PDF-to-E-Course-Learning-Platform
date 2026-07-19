"""Upload repository."""
from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.models.upload import Upload
from app.repositories.base import BaseRepository


class UploadRepository(BaseRepository[Upload]):
    def __init__(self, db: Session) -> None:
        super().__init__(Upload, db)

    def list_for_user(self, user_id: uuid.UUID, *, limit: int = 100, offset: int = 0) -> Sequence[Upload]:
        return self.find_all(
            Upload.user_id == user_id,
            order_by=Upload.created_at.desc(),
            limit=limit,
            offset=offset,
        )

    def get_for_user(self, upload_id: uuid.UUID, user_id: uuid.UUID) -> Upload | None:
        return self.find_one(Upload.id == upload_id, Upload.user_id == user_id)

    def count_for_user(self, user_id: uuid.UUID) -> int:
        return self.count_where(Upload.user_id == user_id)
