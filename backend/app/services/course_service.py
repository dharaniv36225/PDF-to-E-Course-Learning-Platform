"""Course service: AI generation and retrieval of courses/chapters/lessons."""
from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.ai.course_generator import generate_course_structure
from app.core.errors import ValidationAppError, get_or_404
from app.core.logging import get_logger
from app.models.course import Chapter, Course, Lesson
from app.repositories.course import CourseRepository, LessonRepository
from app.repositories.progress import ProgressRepository
from app.repositories.upload import UploadRepository
from app.services.progress_service import summarize_lesson_progress

logger = get_logger(__name__)


class CourseService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.courses = CourseRepository(db)
        self.lessons = LessonRepository(db)
        self.uploads = UploadRepository(db)
        self.progress = ProgressRepository(db)

    async def generate_from_upload(
        self,
        user_id: uuid.UUID,
        upload_id: uuid.UUID,
        *,
        difficulty: str | None = None,
        max_chapters: int | None = None,
    ) -> Course:
        upload = get_or_404(self.uploads.get_for_user(upload_id, user_id), "Upload not found")
        if upload.status != "ready" or not upload.extracted_text:
            raise ValidationAppError("Upload is not ready for course generation")

        structure = await generate_course_structure(
            upload.extracted_text,
            difficulty=difficulty or "beginner",
            max_chapters=max_chapters or 8,
        )

        course = Course(
            user_id=user_id,
            upload_id=upload_id,
            title=structure["title"],
            description=structure.get("description"),
            difficulty=structure.get("difficulty", "beginner"),
            estimated_minutes=int(structure.get("estimated_minutes") or 0),
            learning_objectives=structure.get("learning_objectives", []),
            prerequisites=structure.get("prerequisites", []),
            tags=structure.get("tags", []),
            status="ready",
        )
        self.courses.add(course)

        for c_idx, chapter_data in enumerate(structure.get("chapters", [])):
            chapter = Chapter(
                course_id=course.id,
                title=chapter_data["title"],
                summary=chapter_data.get("summary"),
                order_index=c_idx,
            )
            self.db.add(chapter)
            self.db.flush()
            for l_idx, lesson_data in enumerate(chapter_data.get("lessons", [])):
                lesson = Lesson(
                    chapter_id=chapter.id,
                    title=lesson_data["title"],
                    explanation=lesson_data.get("explanation"),
                    examples=lesson_data.get("examples"),
                    important_notes=lesson_data.get("important_notes"),
                    summary=lesson_data.get("summary"),
                    content=lesson_data.get("explanation"),
                    key_takeaways=lesson_data.get("key_takeaways", []),
                    estimated_minutes=int(lesson_data.get("estimated_minutes") or 5),
                    order_index=l_idx,
                )
                self.db.add(lesson)
        self.courses.commit()
        self.db.refresh(course)
        return course

    def list_courses(self, user_id: uuid.UUID) -> Sequence[Course]:
        return self.courses.list_for_user(user_id)

    def get_course(self, course_id: uuid.UUID, user_id: uuid.UUID) -> Course:
        return get_or_404(self.courses.get_detail(course_id, user_id), "Course not found")

    def get_lessons(self, course_id: uuid.UUID) -> Sequence[Lesson]:
        return self.lessons.list_for_course(course_id)

    def get_lesson(self, lesson_id: uuid.UUID, course_id: uuid.UUID) -> Lesson:
        return get_or_404(self.lessons.get_in_course(lesson_id, course_id), "Lesson not found")

    def delete_course(self, course_id: uuid.UUID, user_id: uuid.UUID) -> None:
        course = get_or_404(self.courses.get_for_user(course_id, user_id), "Course not found")
        self.courses.delete(course)
        self.courses.commit()

    def compute_progress(self, user_id: uuid.UUID, course_id: uuid.UUID) -> dict:
        lessons = self.lessons.list_for_course(course_id)
        progress_rows = self.progress.list_for_course(user_id, course_id)
        return summarize_lesson_progress(len(lessons), progress_rows)

    def list_courses_with_progress(self, user_id: uuid.UUID) -> list[dict]:
        courses = self.courses.list_for_user(user_id)
        results = []
        for course in courses:
            stats = self.compute_progress(user_id, course.id)
            results.append({"course": course, "stats": stats})
        return results
