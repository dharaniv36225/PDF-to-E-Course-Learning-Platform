"""Search service combining keyword search (Postgres) and semantic search (Chroma)."""
from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.ai.vector_store import get_vector_store
from app.core.logging import get_logger
from app.models.course import Chapter, Course, Lesson
from app.repositories.course import CourseRepository

logger = get_logger(__name__)


class SearchService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.courses = CourseRepository(db)
        self.vector_store = get_vector_store()

    def search(self, user_id: uuid.UUID, query: str, course_id: uuid.UUID | None = None) -> dict:
        return {
            "query": query,
            "keyword_results": self._keyword(user_id, query, course_id),
            "semantic_results": self._semantic(user_id, query, course_id),
        }

    def _keyword(self, user_id: uuid.UUID, query: str, course_id: uuid.UUID | None) -> list[dict]:
        like = f"%{query}%"
        results: list[dict] = []

        course_stmt = select(Course).where(
            Course.user_id == user_id,
            or_(Course.title.ilike(like), Course.description.ilike(like)),
        )
        if course_id:
            course_stmt = course_stmt.where(Course.id == course_id)
        for course in self.db.execute(course_stmt.limit(10)).scalars().all():
            results.append(
                {
                    "type": "course",
                    "id": course.id,
                    "title": course.title,
                    "snippet": (course.description or "")[:200],
                    "course_id": course.id,
                }
            )

        chapter_stmt = (
            select(Chapter)
            .join(Course, Chapter.course_id == Course.id)
            .where(Course.user_id == user_id, Chapter.title.ilike(like))
        )
        if course_id:
            chapter_stmt = chapter_stmt.where(Course.id == course_id)
        for chapter in self.db.execute(chapter_stmt.limit(10)).scalars().all():
            results.append(
                {
                    "type": "chapter",
                    "id": chapter.id,
                    "title": chapter.title,
                    "snippet": (chapter.summary or "")[:200],
                    "course_id": chapter.course_id,
                }
            )

        lesson_stmt = (
            select(Lesson, Chapter.course_id)
            .join(Chapter, Lesson.chapter_id == Chapter.id)
            .join(Course, Chapter.course_id == Course.id)
            .where(
                Course.user_id == user_id,
                or_(Lesson.title.ilike(like), Lesson.content.ilike(like)),
            )
        )
        if course_id:
            lesson_stmt = lesson_stmt.where(Course.id == course_id)
        for lesson, c_id in self.db.execute(lesson_stmt.limit(15)).all():
            results.append(
                {
                    "type": "lesson",
                    "id": lesson.id,
                    "title": lesson.title,
                    "snippet": (lesson.summary or lesson.content or "")[:200],
                    "course_id": c_id,
                }
            )
        return results

    def _semantic(self, user_id: uuid.UUID, query: str, course_id: uuid.UUID | None) -> list[dict]:
        courses = (
            [self.courses.get_for_user(course_id, user_id)]
            if course_id
            else list(self.courses.list_for_user(user_id))
        )
        results: list[dict] = []
        seen_uploads: set[str] = set()
        for course in courses:
            if not course or str(course.upload_id) in seen_uploads:
                continue
            seen_uploads.add(str(course.upload_id))
            try:
                chunks = self.vector_store.query(str(course.upload_id), query, top_k=4)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Semantic search failed for %s: %s", course.upload_id, exc)
                continue
            for chunk in chunks:
                results.append(
                    {
                        "type": "document",
                        "id": course.id,
                        "title": course.title,
                        "snippet": chunk["content"][:240],
                        "course_id": course.id,
                        "score": chunk.get("score"),
                    }
                )
        results.sort(key=lambda r: r.get("score") or 0, reverse=True)
        return results[:10]
