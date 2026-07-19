"""Regression tests for quiz access-control (IDOR) enforcement."""
from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest

from app.core.errors import NotFoundError
from app.services.quiz_service import QuizService


class _StubQuizRepo:
    def __init__(self, quiz: object | None) -> None:
        self._quiz = quiz

    def get_detail(self, quiz_id: uuid.UUID) -> object | None:
        return self._quiz


class _StubCourseRepo:
    def __init__(self, owned: bool) -> None:
        self._owned = owned

    def get_for_user(self, course_id: uuid.UUID, user_id: uuid.UUID) -> object | None:
        return SimpleNamespace(id=course_id) if self._owned else None


def _service(quiz: object | None, owned: bool) -> QuizService:
    service = QuizService.__new__(QuizService)
    service.quizzes = _StubQuizRepo(quiz)
    service.courses = _StubCourseRepo(owned)
    return service


def test_get_detail_rejects_quiz_owned_by_another_user() -> None:
    quiz = SimpleNamespace(id=uuid.uuid4(), course_id=uuid.uuid4())
    service = _service(quiz, owned=False)
    with pytest.raises(NotFoundError):
        service.get_detail(quiz.id, uuid.uuid4())


def test_get_detail_allows_owner() -> None:
    quiz = SimpleNamespace(id=uuid.uuid4(), course_id=uuid.uuid4())
    service = _service(quiz, owned=True)
    assert service.get_detail(quiz.id, uuid.uuid4()) is quiz


def test_get_detail_missing_quiz_raises_not_found() -> None:
    service = _service(None, owned=True)
    with pytest.raises(NotFoundError):
        service.get_detail(uuid.uuid4(), uuid.uuid4())
