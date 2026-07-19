"""Learning progress routes."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.progress import (
    CourseProgressSummary,
    LessonProgressRead,
    LessonProgressUpdate,
)
from app.services.progress_service import ProgressService

router = APIRouter(prefix="/progress", tags=["progress"])


@router.put(
    "/courses/{course_id}/lessons/{lesson_id}",
    response_model=LessonProgressRead,
)
def update_lesson_progress(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    payload: LessonProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LessonProgressRead:
    return LessonProgressRead.model_validate(
        ProgressService(db).update_lesson_progress(
            current_user.id,
            course_id,
            lesson_id,
            completed=payload.completed,
            time_spent_seconds=payload.time_spent_seconds,
            last_position=payload.last_position,
        )
    )


@router.get("/courses/{course_id}", response_model=CourseProgressSummary)
def course_progress(
    course_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CourseProgressSummary:
    return CourseProgressSummary.model_validate(
        ProgressService(db).get_course_summary(current_user.id, course_id)
    )
