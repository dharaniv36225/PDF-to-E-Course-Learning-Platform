"""Integration tests for ProgressService (requires the configured database)."""
import uuid

import pytest

from app.core.errors import NotFoundError
from app.services.progress_service import ProgressService


def test_update_creates_progress_record(db, user, make_course, make_lesson):
    course = make_course()
    lesson = make_lesson(course)
    service = ProgressService(db)

    record = service.update_lesson_progress(
        user.id, course.id, lesson.id, completed=True, time_spent_seconds=30
    )

    assert record.completed is True
    assert record.completed_at is not None
    assert record.time_spent_seconds == 30


def test_update_accumulates_time_and_toggles_completion(db, user, make_course, make_lesson):
    course = make_course()
    lesson = make_lesson(course)
    service = ProgressService(db)

    service.update_lesson_progress(user.id, course.id, lesson.id, time_spent_seconds=10)
    record = service.update_lesson_progress(
        user.id, course.id, lesson.id, time_spent_seconds=15, last_position=42
    )

    assert record.time_spent_seconds == 25
    assert record.last_position == 42

    reopened = service.update_lesson_progress(user.id, course.id, lesson.id, completed=False)
    assert reopened.completed is False
    assert reopened.completed_at is None


def test_update_unknown_course_raises(db, user):
    service = ProgressService(db)
    with pytest.raises(NotFoundError):
        service.update_lesson_progress(user.id, uuid.uuid4(), uuid.uuid4(), completed=True)


def test_update_unknown_lesson_raises(db, user, make_course):
    course = make_course()
    service = ProgressService(db)
    with pytest.raises(NotFoundError):
        service.update_lesson_progress(user.id, course.id, uuid.uuid4(), completed=True)


def test_course_summary_computes_completion_percent(db, user, make_course, make_lesson):
    course = make_course()
    lesson_a = make_lesson(course)
    lesson_b = make_lesson(course)
    service = ProgressService(db)

    service.update_lesson_progress(user.id, course.id, lesson_a.id, completed=True, time_spent_seconds=60)
    service.update_lesson_progress(user.id, course.id, lesson_b.id, time_spent_seconds=40)

    summary = service.get_course_summary(user.id, course.id)

    assert summary["total_lessons"] == 2
    assert summary["completed_lessons"] == 1
    assert summary["completion_percent"] == 50.0
    assert summary["total_time_spent_seconds"] == 100


def test_course_summary_unknown_course_raises(db, user):
    service = ProgressService(db)
    with pytest.raises(NotFoundError):
        service.get_course_summary(user.id, uuid.uuid4())
