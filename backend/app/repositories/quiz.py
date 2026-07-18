"""Quiz repositories."""
from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.quiz import Quiz, QuizAttempt, QuizQuestion
from app.repositories.base import BaseRepository


class QuizRepository(BaseRepository[Quiz]):
    def __init__(self, db: Session) -> None:
        super().__init__(Quiz, db)

    def list_for_course(self, course_id: uuid.UUID) -> Sequence[Quiz]:
        stmt = (
            select(Quiz)
            .where(Quiz.course_id == course_id)
            .order_by(Quiz.created_at.desc())
        )
        return self.db.execute(stmt).scalars().all()

    def get_detail(self, quiz_id: uuid.UUID) -> Quiz | None:
        stmt = (
            select(Quiz)
            .where(Quiz.id == quiz_id)
            .options(selectinload(Quiz.questions))
        )
        return self.db.execute(stmt).scalar_one_or_none()


class QuizQuestionRepository(BaseRepository[QuizQuestion]):
    def __init__(self, db: Session) -> None:
        super().__init__(QuizQuestion, db)


class QuizAttemptRepository(BaseRepository[QuizAttempt]):
    def __init__(self, db: Session) -> None:
        super().__init__(QuizAttempt, db)

    def list_for_user(self, user_id: uuid.UUID) -> Sequence[QuizAttempt]:
        stmt = (
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.created_at.desc())
        )
        return self.db.execute(stmt).scalars().all()
