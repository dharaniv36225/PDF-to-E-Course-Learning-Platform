"""Progress schemas."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class LessonProgressUpdate(BaseModel):
    completed: bool | None = None
    time_spent_seconds: int | None = Field(default=None, ge=0)
    last_position: int | None = Field(default=None, ge=0)


class LessonProgressRead(ORMModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    completed: bool
    completed_at: datetime | None = None
    time_spent_seconds: int
    last_position: int


class CourseProgressSummary(BaseModel):
    course_id: uuid.UUID
    total_lessons: int
    completed_lessons: int
    completion_percent: float
    total_time_spent_seconds: int
