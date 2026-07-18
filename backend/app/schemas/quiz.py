"""Quiz schemas."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class QuizQuestionRead(ORMModel):
    id: uuid.UUID
    question_type: str
    question: str
    options: list[str] | None = None
    order_index: int


class QuizQuestionWithAnswer(QuizQuestionRead):
    correct_answer: str
    explanation: str | None = None


class QuizRead(ORMModel):
    id: uuid.UUID
    course_id: uuid.UUID
    chapter_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    difficulty: str
    created_at: datetime


class QuizDetail(QuizRead):
    questions: list[QuizQuestionRead] = []


class GenerateQuizRequest(BaseModel):
    course_id: uuid.UUID
    chapter_id: uuid.UUID | None = None
    num_questions: int = Field(default=5, ge=1, le=20)
    question_types: list[str] = Field(default_factory=lambda: ["mcq", "true_false", "short_answer"])


class SubmittedAnswer(BaseModel):
    question_id: uuid.UUID
    answer: str


class QuizSubmission(BaseModel):
    answers: list[SubmittedAnswer]


class GradedAnswer(BaseModel):
    question_id: uuid.UUID
    question: str
    submitted_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str | None = None


class QuizAttemptResult(ORMModel):
    id: uuid.UUID
    quiz_id: uuid.UUID
    score: float
    total_questions: int
    correct_count: int
    created_at: datetime
    graded: list[GradedAnswer] = []
