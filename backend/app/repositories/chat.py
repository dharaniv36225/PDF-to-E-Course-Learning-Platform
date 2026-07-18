"""Chat session and message repositories."""
from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.chat import ChatMessage, ChatSession
from app.repositories.base import BaseRepository


class ChatSessionRepository(BaseRepository[ChatSession]):
    def __init__(self, db: Session) -> None:
        super().__init__(ChatSession, db)

    def list_for_user(self, user_id: uuid.UUID, *, course_id: uuid.UUID | None = None) -> Sequence[ChatSession]:
        stmt = select(ChatSession).where(ChatSession.user_id == user_id)
        if course_id is not None:
            stmt = stmt.where(ChatSession.course_id == course_id)
        stmt = stmt.order_by(ChatSession.created_at.desc())
        return self.db.execute(stmt).scalars().all()

    def get_for_user(self, session_id: uuid.UUID, user_id: uuid.UUID) -> ChatSession | None:
        stmt = select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_detail(self, session_id: uuid.UUID, user_id: uuid.UUID) -> ChatSession | None:
        stmt = (
            select(ChatSession)
            .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .options(selectinload(ChatSession.messages))
        )
        return self.db.execute(stmt).scalar_one_or_none()


class ChatMessageRepository(BaseRepository[ChatMessage]):
    def __init__(self, db: Session) -> None:
        super().__init__(ChatMessage, db)

    def list_for_session(self, session_id: uuid.UUID) -> Sequence[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )
        return self.db.execute(stmt).scalars().all()
