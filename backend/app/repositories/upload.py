"""Upload repository."""
from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.upload import Upload
from app.repositories.base import BaseRepository


class UploadRepository(BaseRepository[Upload]):
    def __init__(self, db: Session) -> None:
        super().__init__(Upload, db)

    def list_for_user(self, user_id: uuid.UUID, *, limit: int = 100, offset: int = 0) -> Sequence[Upload]:
        stmt = (
            select(Upload)
            .where(Upload.user_id == user_id)
            .order_by(Upload.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.db.execute(stmt).scalars().all()

    def get_for_user(self, upload_id: uuid.UUID, user_id: uuid.UUID) -> Upload | None:
        stmt = select(Upload).where(Upload.id == upload_id, Upload.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def count_for_user(self, user_id: uuid.UUID) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(Upload).where(Upload.user_id == user_id)
        return self.db.execute(stmt).scalar_one()
