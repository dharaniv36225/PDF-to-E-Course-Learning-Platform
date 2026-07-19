"""Quiz repositories."""
from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy.orm import Session, selectinload

from app.models.quiz import Quiz, QuizAttempt, QuizQuestion
from app.repositories.base import BaseRepository


class QuizRepository(BaseRepository[Quiz]):
    def __init__(self, db: Session) -> None:
        super().__init__(Quiz, db)

    def list_for_course(self, course_id: uuid.UUID) -> Sequence[Quiz]:
        return self.find_all(Quiz.course_id == course_id, order_by=Quiz.created_at.desc())

    def get_detail(self, quiz_id: uuid.UUID) -> Quiz | None:
        return self.find_one(Quiz.id == quiz_id, options=[selectinload(Quiz.questions)])


class QuizQuestionRepository(BaseRepository[QuizQuestion]):
    def __init__(self, db: Session) -> None:
        super().__init__(QuizQuestion, db)


class QuizAttemptRepository(BaseRepository[QuizAttempt]):
    def __init__(self, db: Session) -> None:
        super().__init__(QuizAttempt, db)

    def list_for_user(self, user_id: uuid.UUID) -> Sequence[QuizAttempt]:
        return self.find_all(QuizAttempt.user_id == user_id, order_by=QuizAttempt.created_at.desc())
