"""User model."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.chat import ChatSession
    from app.models.course import Course
    from app.models.progress import LessonProgress
    from app.models.quiz import QuizAttempt
    from app.models.upload import Upload


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    auth_provider: Mapped[str] = mapped_column(String(50), default="email", nullable=False)
    supabase_user_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    uploads: Mapped[list[Upload]] = relationship(back_populates="user", cascade="all, delete-orphan")
    courses: Mapped[list[Course]] = relationship(back_populates="user", cascade="all, delete-orphan")
    progress: Mapped[list[LessonProgress]] = relationship(back_populates="user", cascade="all, delete-orphan")
    chat_sessions: Mapped[list[ChatSession]] = relationship(back_populates="user", cascade="all, delete-orphan")
    quiz_attempts: Mapped[list[QuizAttempt]] = relationship(back_populates="user", cascade="all, delete-orphan")
