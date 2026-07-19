"""Shared fixtures and factory helpers for the test suite.

Fixtures that touch the database require the configured Postgres instance
(``DATABASE_URL``) with migrations applied; see the repo's ``db`` env note.
"""
from __future__ import annotations

import uuid
from collections.abc import Callable, Iterator

import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.chat import ChatMessage, ChatSession
from app.models.course import Chapter, Course, Lesson
from app.models.upload import Upload
from app.models.user import User


@pytest.fixture
def db() -> Iterator[Session]:
    """A database session that is closed at the end of the test."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def user(db: Session) -> Iterator[User]:
    """A persisted user; deleted (cascading) at teardown."""
    record = User(
        email=f"user-{uuid.uuid4()}@test.dev",
        full_name="Test User",
        auth_provider="email",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    yield record
    db.delete(record)
    db.commit()


@pytest.fixture
def make_upload(db: Session, user: User) -> Callable[..., Upload]:
    def _make(**overrides) -> Upload:
        fields = {
            "user_id": user.id,
            "filename": "doc.pdf",
            "original_filename": "doc.pdf",
            "storage_path": "/tmp/doc.pdf",
            "storage_provider": "local",
            "status": "ready",
        }
        fields.update(overrides)
        upload = Upload(**fields)
        db.add(upload)
        db.commit()
        db.refresh(upload)
        return upload

    return _make


@pytest.fixture
def make_course(db: Session, user: User, make_upload: Callable[..., Upload]) -> Callable[..., Course]:
    def _make(*, upload: Upload | None = None, **overrides) -> Course:
        upload = upload or make_upload()
        fields = {
            "user_id": user.id,
            "upload_id": upload.id,
            "title": "Test Course",
            "difficulty": "beginner",
            "status": "ready",
        }
        fields.update(overrides)
        course = Course(**fields)
        db.add(course)
        db.commit()
        db.refresh(course)
        return course

    return _make


@pytest.fixture
def make_lesson(db: Session) -> Callable[..., Lesson]:
    """Create a chapter+lesson under a course and return the lesson."""

    def _make(course: Course, **overrides) -> Lesson:
        chapter = Chapter(course_id=course.id, title="Chapter 1", order_index=0)
        db.add(chapter)
        db.commit()
        db.refresh(chapter)
        fields = {
            "chapter_id": chapter.id,
            "title": "Lesson 1",
            "content": "Lesson body",
            "order_index": 0,
        }
        fields.update(overrides)
        lesson = Lesson(**fields)
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        return lesson

    return _make


@pytest.fixture
def make_chat_session(db: Session, user: User) -> Callable[..., ChatSession]:
    def _make(course: Course, **overrides) -> ChatSession:
        session = ChatSession(
            user_id=user.id,
            course_id=course.id,
            title=overrides.pop("title", "Conversation"),
            **overrides,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    return _make


__all__ = ["ChatMessage"]
