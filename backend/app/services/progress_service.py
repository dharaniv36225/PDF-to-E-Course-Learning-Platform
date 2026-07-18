"""Learning progress service."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.progress import LessonProgress
from app.repositories.course import CourseRepository, LessonRepository
from app.repositories.progress import ProgressRepository


class ProgressService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.progress = ProgressRepository(db)
        self.lessons = LessonRepository(db)
        self.courses = CourseRepository(db)

    def update_lesson_progress(
        self,
        user_id: uuid.UUID,
        course_id: uuid.UUID,
        lesson_id: uuid.UUID,
        *,
        completed: bool | None = None,
        time_spent_seconds: int | None = None,
        last_position: int | None = None,
    ) -> LessonProgress:
        if not self.courses.get_for_user(course_id, user_id):
            raise NotFoundError("Course not found")
        if not self.lessons.get_in_course(lesson_id, course_id):
            raise NotFoundError("Lesson not found")

        record = self.progress.get_for_lesson(user_id, lesson_id)
        if record is None:
            record = LessonProgress(user_id=user_id, lesson_id=lesson_id)
            self.progress.add(record)

        if completed is not None:
            record.completed = completed
            record.completed_at = datetime.now(timezone.utc) if completed else None
        if time_spent_seconds is not None:
            record.time_spent_seconds = record.time_spent_seconds + time_spent_seconds
        if last_position is not None:
            record.last_position = last_position
        self.progress.commit()
        return record

    def get_course_summary(self, user_id: uuid.UUID, course_id: uuid.UUID) -> dict:
        if not self.courses.get_for_user(course_id, user_id):
            raise NotFoundError("Course not found")
        lessons = self.lessons.list_for_course(course_id)
        total = len(lessons)
        rows = self.progress.list_for_course(user_id, course_id)
        completed = sum(1 for r in rows if r.completed)
        time_spent = sum(r.time_spent_seconds for r in rows)
        percent = round((completed / total) * 100, 2) if total else 0.0
        return {
            "course_id": course_id,
            "total_lessons": total,
            "completed_lessons": completed,
            "completion_percent": percent,
            "total_time_spent_seconds": time_spent,
        }
