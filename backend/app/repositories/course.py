"""Course, chapter and lesson repositories."""
from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.course import Chapter, Course, Lesson
from app.repositories.base import BaseRepository


class CourseRepository(BaseRepository[Course]):
    def __init__(self, db: Session) -> None:
        super().__init__(Course, db)

    def list_for_user(self, user_id: uuid.UUID, *, limit: int = 100, offset: int = 0) -> Sequence[Course]:
        stmt = (
            select(Course)
            .where(Course.user_id == user_id)
            .order_by(Course.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.db.execute(stmt).scalars().all()

    def get_for_user(self, course_id: uuid.UUID, user_id: uuid.UUID) -> Course | None:
        stmt = select(Course).where(Course.id == course_id, Course.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_detail(self, course_id: uuid.UUID, user_id: uuid.UUID) -> Course | None:
        stmt = (
            select(Course)
            .where(Course.id == course_id, Course.user_id == user_id)
            .options(selectinload(Course.chapters).selectinload(Chapter.lessons))
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def count_for_user(self, user_id: uuid.UUID) -> int:
        stmt = select(func.count()).select_from(Course).where(Course.user_id == user_id)
        return self.db.execute(stmt).scalar_one()


class ChapterRepository(BaseRepository[Chapter]):
    def __init__(self, db: Session) -> None:
        super().__init__(Chapter, db)


class LessonRepository(BaseRepository[Lesson]):
    def __init__(self, db: Session) -> None:
        super().__init__(Lesson, db)

    def list_for_course(self, course_id: uuid.UUID) -> Sequence[Lesson]:
        stmt = (
            select(Lesson)
            .join(Chapter, Lesson.chapter_id == Chapter.id)
            .where(Chapter.course_id == course_id)
            .order_by(Chapter.order_index, Lesson.order_index)
        )
        return self.db.execute(stmt).scalars().all()

    def get_in_course(self, lesson_id: uuid.UUID, course_id: uuid.UUID) -> Lesson | None:
        stmt = (
            select(Lesson)
            .join(Chapter, Lesson.chapter_id == Chapter.id)
            .where(Lesson.id == lesson_id, Chapter.course_id == course_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()
