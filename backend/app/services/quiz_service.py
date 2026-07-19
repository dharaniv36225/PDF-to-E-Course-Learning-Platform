"""Quiz service: AI generation, retrieval, grading and attempts."""
from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.ai.quiz_generator import generate_quiz
from app.core.errors import NotFoundError, ValidationAppError
from app.models.quiz import Quiz, QuizAttempt, QuizQuestion
from app.repositories.course import CourseRepository, LessonRepository
from app.repositories.quiz import QuizAttemptRepository, QuizRepository
from app.repositories.upload import UploadRepository


class QuizService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.quizzes = QuizRepository(db)
        self.attempts = QuizAttemptRepository(db)
        self.courses = CourseRepository(db)
        self.lessons = LessonRepository(db)
        self.uploads = UploadRepository(db)

    def _course_or_404(self, course_id: uuid.UUID, user_id: uuid.UUID):
        course = self.courses.get_for_user(course_id, user_id)
        if not course:
            raise NotFoundError("Course not found")
        return course

    def _source_material(self, course, chapter_id: uuid.UUID | None) -> str:
        if chapter_id is not None:
            lessons = [
                lesson
                for lesson in self.lessons.list_for_course(course.id)
                if lesson.chapter_id == chapter_id
            ]
            material = "\n\n".join(
                f"{lesson.title}\n{lesson.explanation or ''}\n{lesson.summary or ''}"
                for lesson in lessons
            )
            if material.strip():
                return material
        upload = self.uploads.get(course.upload_id)
        return (upload.extracted_text if upload else "") or ""

    async def generate(
        self,
        user_id: uuid.UUID,
        course_id: uuid.UUID,
        *,
        chapter_id: uuid.UUID | None = None,
        num_questions: int = 5,
        question_types: list[str] | None = None,
    ) -> Quiz:
        course = self._course_or_404(course_id, user_id)
        material = self._source_material(course, chapter_id)
        if not material.strip():
            raise ValidationAppError("No source material available to generate a quiz")

        data = await generate_quiz(
            material, num_questions=num_questions, question_types=question_types
        )
        quiz = Quiz(
            course_id=course_id,
            chapter_id=chapter_id,
            title=data.get("title", "Quiz"),
            description=data.get("description"),
            difficulty=course.difficulty,
        )
        self.quizzes.add(quiz)
        for idx, q in enumerate(data.get("questions", [])):
            self.db.add(
                QuizQuestion(
                    quiz_id=quiz.id,
                    question_type=q["question_type"],
                    question=q["question"],
                    options=q.get("options", []),
                    correct_answer=q["correct_answer"],
                    explanation=q.get("explanation"),
                    order_index=idx,
                )
            )
        self.quizzes.commit()
        self.db.refresh(quiz)
        return self.get_detail(quiz.id, user_id)

    def list_for_course(self, course_id: uuid.UUID, user_id: uuid.UUID) -> Sequence[Quiz]:
        self._course_or_404(course_id, user_id)
        return self.quizzes.list_for_course(course_id)

    def get_detail(self, quiz_id: uuid.UUID, user_id: uuid.UUID) -> Quiz:
        quiz = self.quizzes.get_detail(quiz_id)
        if not quiz:
            raise NotFoundError("Quiz not found")
        # Enforce ownership: the quiz's course must belong to the requesting user.
        self._course_or_404(quiz.course_id, user_id)
        return quiz

    def grade(self, quiz_id: uuid.UUID, user_id: uuid.UUID, submitted: list[dict]) -> dict:
        quiz = self.get_detail(quiz_id, user_id)
        answers_by_qid = {str(a["question_id"]): a["answer"] for a in submitted}
        graded: list[dict] = []
        correct_count = 0
        for question in quiz.questions:
            submitted_answer = answers_by_qid.get(str(question.id), "")
            is_correct = self._is_correct(question, submitted_answer)
            if is_correct:
                correct_count += 1
            graded.append(
                {
                    "question_id": question.id,
                    "question": question.question,
                    "submitted_answer": submitted_answer,
                    "correct_answer": question.correct_answer,
                    "is_correct": is_correct,
                    "explanation": question.explanation,
                }
            )
        total = len(quiz.questions)
        score = round((correct_count / total) * 100, 2) if total else 0.0
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            user_id=user_id,
            score=score,
            total_questions=total,
            correct_count=correct_count,
            answers=submitted,
        )
        self.attempts.add(attempt)
        self.attempts.commit()
        return {"attempt": attempt, "graded": graded}

    @staticmethod
    def _is_correct(question: QuizQuestion, submitted: str) -> bool:
        expected = (question.correct_answer or "").strip().lower()
        given = (submitted or "").strip().lower()
        if not given:
            return False
        if question.question_type == "short_answer":
            return expected in given or given in expected
        return expected == given

    def list_attempts(self, user_id: uuid.UUID) -> Sequence[QuizAttempt]:
        return self.attempts.list_for_user(user_id)
