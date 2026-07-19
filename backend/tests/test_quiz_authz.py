"""Authorization/ownership tests for quiz endpoints (requires the configured database).

Regression: quiz detail/submit endpoints did not verify that the quiz belonged to
a course owned by the caller (IDOR). Any authenticated user could read another
user's quiz and submit attempts against it.
"""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.main import app
from app.models.course import Course
from app.models.quiz import Quiz, QuizQuestion
from app.models.upload import Upload
from app.models.user import User

client = TestClient(app)


def _auth(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(str(user.id))}"}


@pytest.fixture()
def two_users_with_quiz():
    """Create an owner (with a quiz) and an unrelated attacker user."""
    db = SessionLocal()
    owner = User(email=f"owner-{uuid.uuid4()}@test.dev", full_name="Owner", auth_provider="email")
    attacker = User(email=f"attacker-{uuid.uuid4()}@test.dev", full_name="Attacker", auth_provider="email")
    db.add_all([owner, attacker])
    db.flush()

    upload = Upload(
        user_id=owner.id,
        filename="doc.pdf",
        original_filename="doc.pdf",
        storage_path="/tmp/doc.pdf",
        status="ready",
    )
    db.add(upload)
    db.flush()

    course = Course(
        user_id=owner.id,
        upload_id=upload.id,
        title="Owner Course",
        difficulty="beginner",
        status="ready",
    )
    db.add(course)
    db.flush()

    quiz = Quiz(course_id=course.id, title="Owner Quiz", difficulty="beginner")
    db.add(quiz)
    db.flush()
    db.add(
        QuizQuestion(
            quiz_id=quiz.id,
            question_type="mcq",
            question="2+2?",
            options=["3", "4"],
            correct_answer="4",
            order_index=0,
        )
    )
    db.commit()

    quiz_id = quiz.id
    question_id = quiz.questions[0].id
    try:
        yield {
            "owner": owner,
            "attacker": attacker,
            "quiz_id": quiz_id,
            "question_id": question_id,
        }
    finally:
        db.delete(owner)  # cascades to upload/course/quiz/questions
        db.delete(attacker)
        db.commit()
        db.close()


def test_get_quiz_requires_authentication(two_users_with_quiz) -> None:
    resp = client.get(f"/api/v1/quizzes/{two_users_with_quiz['quiz_id']}")
    assert resp.status_code == 401


def test_owner_can_read_quiz(two_users_with_quiz) -> None:
    ctx = two_users_with_quiz
    resp = client.get(f"/api/v1/quizzes/{ctx['quiz_id']}", headers=_auth(ctx["owner"]))
    assert resp.status_code == 200
    assert resp.json()["title"] == "Owner Quiz"


def test_non_owner_cannot_read_quiz(two_users_with_quiz) -> None:
    ctx = two_users_with_quiz
    resp = client.get(f"/api/v1/quizzes/{ctx['quiz_id']}", headers=_auth(ctx["attacker"]))
    assert resp.status_code == 403


def test_missing_quiz_returns_404(two_users_with_quiz) -> None:
    ctx = two_users_with_quiz
    resp = client.get(f"/api/v1/quizzes/{uuid.uuid4()}", headers=_auth(ctx["owner"]))
    assert resp.status_code == 404


def test_owner_can_submit_quiz(two_users_with_quiz) -> None:
    ctx = two_users_with_quiz
    resp = client.post(
        f"/api/v1/quizzes/{ctx['quiz_id']}/submit",
        headers=_auth(ctx["owner"]),
        json={"answers": [{"question_id": str(ctx["question_id"]), "answer": "4"}]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["score"] == 100
    assert body["graded"][0]["is_correct"] is True


def test_non_owner_cannot_submit_quiz(two_users_with_quiz) -> None:
    ctx = two_users_with_quiz
    resp = client.post(
        f"/api/v1/quizzes/{ctx['quiz_id']}/submit",
        headers=_auth(ctx["attacker"]),
        json={"answers": [{"question_id": str(ctx["question_id"]), "answer": "4"}]},
    )
    assert resp.status_code == 403
