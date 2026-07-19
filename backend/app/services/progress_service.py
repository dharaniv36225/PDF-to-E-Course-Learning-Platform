"""Learning progress service."""
from __future__ import annotations

import uuid
from collections.abc import Iterable
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.errors import get_or_404
from app.models.progress import LessonProgress
from app.repositories.course import CourseRepository, LessonRepository
from app.repositories.progress import ProgressRepository


def summarize_lesson_progress(
    total_lessons: int, progress_rows: Iterable[LessonProgress]
) -> dict:
    """Aggregate completion and time-spent metrics for a set of lesson-progress rows."""
    rows = list(progress_rows)
    completed = sum(1 for r in rows if r.completed)
    time_spent = sum(r.time_spent_seconds for r in rows)
    percent = round((completed / total_lessons) * 100, 2) if total_lessons else 0.0
    return {
        "total_lessons": total_lessons,
        "completed_lessons": completed,
        "completion_percent": percent,
        "total_time_spent_seconds": time_spent,
    }


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
        get_or_404(self.courses.get_for_user(course_id, user_id), "Course not found")
        get_or_404(self.lessons.get_in_course(lesson_id, course_id), "Lesson not found")

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
        get_or_404(self.courses.get_for_user(course_id, user_id), "Course not found")
        lessons = self.lessons.list_for_course(course_id)
        rows = self.progress.list_for_course(user_id, course_id)
        return {
            "course_id": course_id,
            **summarize_lesson_progress(len(lessons), rows),
        }
