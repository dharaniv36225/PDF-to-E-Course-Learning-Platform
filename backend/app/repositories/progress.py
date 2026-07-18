"""Lesson progress repository."""
from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.course import Chapter, Lesson
from app.models.progress import LessonProgress
from app.repositories.base import BaseRepository


class ProgressRepository(BaseRepository[LessonProgress]):
    def __init__(self, db: Session) -> None:
        super().__init__(LessonProgress, db)

    def get_for_lesson(self, user_id: uuid.UUID, lesson_id: uuid.UUID) -> LessonProgress | None:
        stmt = select(LessonProgress).where(
            LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_for_course(self, user_id: uuid.UUID, course_id: uuid.UUID) -> Sequence[LessonProgress]:
        stmt = (
            select(LessonProgress)
            .join(Lesson, LessonProgress.lesson_id == Lesson.id)
            .join(Chapter, Lesson.chapter_id == Chapter.id)
            .where(LessonProgress.user_id == user_id, Chapter.course_id == course_id)
        )
        return self.db.execute(stmt).scalars().all()

    def list_for_user(self, user_id: uuid.UUID) -> Sequence[LessonProgress]:
        stmt = select(LessonProgress).where(LessonProgress.user_id == user_id)
        return self.db.execute(stmt).scalars().all()
