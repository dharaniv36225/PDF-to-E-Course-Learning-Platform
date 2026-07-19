"""Course, chapter and lesson routes."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import Message
from app.schemas.course import (
    CourseDetail,
    CourseRead,
    CourseWithProgress,
    GenerateCourseRequest,
    LessonRead,
)
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/generate", response_model=CourseDetail, status_code=status.HTTP_201_CREATED)
async def generate_course(
    payload: GenerateCourseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CourseDetail:
    """Generate a full course (chapters, lessons, summaries) from an uploaded PDF."""
    service = CourseService(db)
    course = await service.generate_from_upload(
        current_user.id,
        payload.upload_id,
        difficulty=payload.difficulty,
        max_chapters=payload.max_chapters,
    )
    return CourseDetail.model_validate(service.get_course(course.id, current_user.id))


@router.get("", response_model=list[CourseWithProgress])
def list_courses(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[CourseWithProgress]:
    service = CourseService(db)
    results = []
    for item in service.list_courses_with_progress(current_user.id):
        course = item["course"]
        stats = item["stats"]
        results.append(
            CourseWithProgress(
                **CourseRead.model_validate(course).model_dump(),
                completion_percent=stats["completion_percent"],
                total_lessons=stats["total_lessons"],
                completed_lessons=stats["completed_lessons"],
            )
        )
    return results


@router.get("/{course_id}", response_model=CourseDetail)
def get_course(
    course_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CourseDetail:
    return CourseDetail.model_validate(CourseService(db).get_course(course_id, current_user.id))


@router.get("/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
def get_lesson(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LessonRead:
    service = CourseService(db)
    service.get_course(course_id, current_user.id)
    return LessonRead.model_validate(service.get_lesson(lesson_id, course_id))


@router.delete("/{course_id}", response_model=Message)
def delete_course(
    course_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Message:
    CourseService(db).delete_course(course_id, current_user.id)
    return Message(message="Course deleted")
