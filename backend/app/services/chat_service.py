"""Chat service backing the RAG chatbot with conversation memory."""
from __future__ import annotations

import uuid
from collections.abc import AsyncIterator, Callable

from sqlalchemy.orm import Session

from app.ai import rag
from app.core.errors import NotFoundError
from app.core.logging import get_logger
from app.models.chat import ChatMessage, ChatSession
from app.repositories.chat import ChatMessageRepository, ChatSessionRepository
from app.repositories.course import CourseRepository

logger = get_logger(__name__)


class ChatService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.sessions = ChatSessionRepository(db)
        self.messages = ChatMessageRepository(db)
        self.courses = CourseRepository(db)

    def _get_course_upload(self, course_id: uuid.UUID, user_id: uuid.UUID) -> uuid.UUID:
        course = self.courses.get_for_user(course_id, user_id)
        if not course:
            raise NotFoundError("Course not found")
        return course.upload_id

    def get_or_create_session(
        self, user_id: uuid.UUID, course_id: uuid.UUID, session_id: uuid.UUID | None, title: str
    ) -> ChatSession:
        if session_id:
            session = self.sessions.get_for_user(session_id, user_id)
            if not session:
                raise NotFoundError("Chat session not found")
            return session
        session = ChatSession(user_id=user_id, course_id=course_id, title=title[:120] or "New conversation")
        self.sessions.add(session)
        self.sessions.commit()
        return session

    def _history(self, session_id: uuid.UUID) -> list[dict]:
        return [
            {"role": m.role, "content": m.content}
            for m in self.messages.list_for_session(session_id)
        ]

    def _save_user_message(self, session_id: uuid.UUID, content: str) -> None:
        self.messages.add(ChatMessage(session_id=session_id, role="user", content=content))
        self.messages.commit()

    def _save_assistant_message(
        self, session_id: uuid.UUID, content: str, sources: list[dict]
    ) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=content,
            sources=sources,
        )
        self.messages.add(message)
        self.messages.commit()
        return message

    async def answer(
        self, user_id: uuid.UUID, course_id: uuid.UUID, session: ChatSession, question: str
    ) -> ChatMessage:
        upload_id = self._get_course_upload(course_id, user_id)
        history = self._history(session.id)
        self._save_user_message(session.id, question)
        text, chunks = await rag.answer(str(upload_id), question, history)
        return self._save_assistant_message(session.id, text, chunks)

    async def stream(
        self, user_id: uuid.UUID, course_id: uuid.UUID, session: ChatSession, question: str
    ) -> tuple[AsyncIterator[str], list[dict], Callable[[str], ChatMessage]]:
        """Return (token_iterator, sources, finalize).

        ``finalize(full_text)`` persists the completed assistant message.
        """
        upload_id = self._get_course_upload(course_id, user_id)
        history = self._history(session.id)
        self._save_user_message(session.id, question)
        iterator, chunks = await rag.stream_answer(str(upload_id), question, history)

        def finalize(full_text: str) -> ChatMessage:
            return self._save_assistant_message(session.id, full_text, chunks)

        return iterator, chunks, finalize

    def list_sessions(self, user_id: uuid.UUID, course_id: uuid.UUID | None = None):
        return self.sessions.list_for_user(user_id, course_id=course_id)

    def get_session_detail(self, session_id: uuid.UUID, user_id: uuid.UUID) -> ChatSession:
        session = self.sessions.get_detail(session_id, user_id)
        if not session:
            raise NotFoundError("Chat session not found")
        return session

    def delete_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> None:
        session = self.sessions.get_for_user(session_id, user_id)
        if not session:
            raise NotFoundError("Chat session not found")
        self.sessions.delete(session)
        self.sessions.commit()
