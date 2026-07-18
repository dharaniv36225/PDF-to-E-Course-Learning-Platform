"""Course, Chapter and Lesson models."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.chat import ChatSession
    from app.models.progress import LessonProgress
    from app.models.quiz import Quiz
    from app.models.upload import Upload
    from app.models.user import User


class Course(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "courses"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("uploads.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(50), default="beginner", nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    learning_objectives: Mapped[list | None] = mapped_column(JSONB, default=list, nullable=True)
    prerequisites: Mapped[list | None] = mapped_column(JSONB, default=list, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSONB, default=list, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="generating", nullable=False)

    user: Mapped[User] = relationship(back_populates="courses")
    upload: Mapped[Upload] = relationship(back_populates="courses")
    chapters: Mapped[list[Chapter]] = relationship(
        back_populates="course", cascade="all, delete-orphan", order_by="Chapter.order_index"
    )
    quizzes: Mapped[list[Quiz]] = relationship(back_populates="course", cascade="all, delete-orphan")
    chat_sessions: Mapped[list[ChatSession]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )


class Chapter(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "chapters"

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    course: Mapped[Course] = relationship(back_populates="chapters")
    lessons: Mapped[list[Lesson]] = relationship(
        back_populates="chapter", cascade="all, delete-orphan", order_by="Lesson.order_index"
    )


class Lesson(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "lessons"

    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    examples: Mapped[str | None] = mapped_column(Text, nullable=True)
    important_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_takeaways: Mapped[list | None] = mapped_column(JSONB, default=list, nullable=True)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    chapter: Mapped[Chapter] = relationship(back_populates="lessons")
    progress: Mapped[list[LessonProgress]] = relationship(
        back_populates="lesson", cascade="all, delete-orphan"
    )
