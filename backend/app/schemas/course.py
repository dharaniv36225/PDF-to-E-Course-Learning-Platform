"""Course, chapter and lesson schemas."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class LessonRead(ORMModel):
    id: uuid.UUID
    chapter_id: uuid.UUID
    title: str
    content: str | None = None
    explanation: str | None = None
    examples: str | None = None
    important_notes: str | None = None
    summary: str | None = None
    key_takeaways: list[str] | None = None
    estimated_minutes: int
    order_index: int


class ChapterRead(ORMModel):
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    summary: str | None = None
    order_index: int
    lessons: list[LessonRead] = []


class CourseRead(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    upload_id: uuid.UUID
    title: str
    description: str | None = None
    difficulty: str
    estimated_minutes: int
    learning_objectives: list[str] | None = None
    prerequisites: list[str] | None = None
    tags: list[str] | None = None
    status: str
    created_at: datetime


class CourseDetail(CourseRead):
    chapters: list[ChapterRead] = []


class CourseWithProgress(CourseRead):
    completion_percent: float = 0.0
    total_lessons: int = 0
    completed_lessons: int = 0

    @classmethod
    def from_course(cls, course: object, stats: dict) -> CourseWithProgress:
        """Build a progress-annotated course from an ORM course and a stats dict."""
        return cls(
            **CourseRead.model_validate(course).model_dump(),
            completion_percent=stats["completion_percent"],
            total_lessons=stats["total_lessons"],
            completed_lessons=stats["completed_lessons"],
        )


class GenerateCourseRequest(BaseModel):
    upload_id: uuid.UUID
    difficulty: str | None = None
    max_chapters: int | None = None
