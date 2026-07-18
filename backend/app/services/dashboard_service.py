"""Dashboard aggregation service."""
from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.repositories.course import CourseRepository
from app.repositories.progress import ProgressRepository
from app.repositories.quiz import QuizAttemptRepository, QuizRepository
from app.repositories.upload import UploadRepository
from app.schemas.course import CourseRead, CourseWithProgress
from app.services.course_service import CourseService


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.courses = CourseRepository(db)
        self.uploads = UploadRepository(db)
        self.attempts = QuizAttemptRepository(db)
        self.quizzes = QuizRepository(db)
        self.progress = ProgressRepository(db)
        self.course_service = CourseService(db)

    def get_stats(self, user_id: uuid.UUID) -> dict:
        total_courses = self.courses.count_for_user(user_id)
        total_uploads = self.uploads.count_for_user(user_id)
        attempts = list(self.attempts.list_for_user(user_id))
        total_attempts = len(attempts)
        avg_score = round(sum(a.score for a in attempts) / total_attempts, 2) if total_attempts else 0.0

        progress_rows = list(self.progress.list_for_user(user_id))
        total_time_minutes = round(sum(r.time_spent_seconds for r in progress_rows) / 60, 2)

        recent_courses = []
        for item in self.course_service.list_courses_with_progress(user_id)[:6]:
            course = item["course"]
            stats = item["stats"]
            recent_courses.append(
                CourseWithProgress(
                    **CourseRead.model_validate(course).model_dump(),
                    completion_percent=stats["completion_percent"],
                    total_lessons=stats["total_lessons"],
                    completed_lessons=stats["completed_lessons"],
                )
            )

        quiz_scores = []
        for attempt in attempts[:20]:
            quiz = self.quizzes.get(attempt.quiz_id)
            quiz_scores.append(
                {
                    "quiz_id": attempt.quiz_id,
                    "quiz_title": quiz.title if quiz else "Quiz",
                    "score": attempt.score,
                    "created_at": attempt.created_at,
                }
            )

        activity = self._activity(progress_rows)
        streak = self._streak({r.updated_at.date() for r in progress_rows if r.completed})

        return {
            "total_courses": total_courses,
            "total_uploads": total_uploads,
            "total_quiz_attempts": total_attempts,
            "average_quiz_score": avg_score,
            "total_time_spent_minutes": total_time_minutes,
            "learning_streak_days": streak,
            "recent_courses": recent_courses,
            "quiz_scores": quiz_scores,
            "activity": activity,
        }

    @staticmethod
    def _activity(progress_rows) -> list:
        buckets: dict[date, float] = defaultdict(float)
        cutoff = datetime.now(timezone.utc).date() - timedelta(days=13)
        for row in progress_rows:
            day = row.updated_at.date()
            if day >= cutoff:
                buckets[day] += row.time_spent_seconds / 60
        result = []
        for i in range(14):
            day = cutoff + timedelta(days=i)
            result.append({"day": day, "minutes": round(buckets.get(day, 0.0), 2)})
        return result

    @staticmethod
    def _streak(active_days: set[date]) -> int:
        if not active_days:
            return 0
        today = datetime.now(timezone.utc).date()
        streak = 0
        cursor = today
        if today not in active_days and (today - timedelta(days=1)) in active_days:
            cursor = today - timedelta(days=1)
        while cursor in active_days:
            streak += 1
            cursor -= timedelta(days=1)
        return streak
