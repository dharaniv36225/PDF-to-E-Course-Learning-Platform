"""Dashboard and search schemas."""
from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.schemas.course import CourseWithProgress


class QuizScorePoint(BaseModel):
    quiz_id: uuid.UUID
    quiz_title: str
    score: float
    created_at: datetime


class DailyActivity(BaseModel):
    day: date
    minutes: float


class DashboardStats(BaseModel):
    total_courses: int
    total_uploads: int
    total_quiz_attempts: int
    average_quiz_score: float
    total_time_spent_minutes: float
    learning_streak_days: int
    recent_courses: list[CourseWithProgress]
    quiz_scores: list[QuizScorePoint]
    activity: list[DailyActivity]


class SearchResultItem(BaseModel):
    type: str  # course | chapter | lesson | document
    id: uuid.UUID
    title: str
    snippet: str | None = None
    course_id: uuid.UUID | None = None
    score: float | None = None


class SearchResponse(BaseModel):
    query: str
    keyword_results: list[SearchResultItem]
    semantic_results: list[SearchResultItem]
