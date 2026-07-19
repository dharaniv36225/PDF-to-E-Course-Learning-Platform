"""Quiz routes."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.quiz import (
    GenerateQuizRequest,
    QuizAttemptResult,
    QuizDetail,
    QuizRead,
    QuizSubmission,
)
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.post("/generate", response_model=QuizDetail, status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    payload: GenerateQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuizDetail:
    service = QuizService(db)
    quiz = await service.generate(
        current_user.id,
        payload.course_id,
        chapter_id=payload.chapter_id,
        num_questions=payload.num_questions,
        question_types=payload.question_types,
    )
    return service.get_detail(quiz.id, current_user.id)


@router.get("/course/{course_id}", response_model=list[QuizRead])
def list_course_quizzes(
    course_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[QuizRead]:
    return list(QuizService(db).list_for_course(course_id, current_user.id))


@router.get("/{quiz_id}", response_model=QuizDetail)
def get_quiz(
    quiz_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuizDetail:
    return QuizService(db).get_detail(quiz_id, current_user.id)


@router.post("/{quiz_id}/submit", response_model=QuizAttemptResult)
def submit_quiz(
    quiz_id: uuid.UUID,
    payload: QuizSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuizAttemptResult:
    service = QuizService(db)
    result = service.grade(quiz_id, current_user.id, [a.model_dump(mode="json") for a in payload.answers])
    attempt = result["attempt"]
    return QuizAttemptResult(
        id=attempt.id,
        quiz_id=attempt.quiz_id,
        score=attempt.score,
        total_questions=attempt.total_questions,
        correct_count=attempt.correct_count,
        created_at=attempt.created_at,
        graded=result["graded"],
    )
