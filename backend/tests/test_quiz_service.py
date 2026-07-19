"""Integration tests for QuizService (requires the configured database)."""
import uuid

import pytest

import app.services.quiz_service as quiz_service_module
from app.core.errors import NotFoundError, ValidationAppError
from app.models.quiz import Quiz, QuizQuestion
from app.services.quiz_service import QuizService


def _make_quiz(db, course, questions):
    quiz = Quiz(course_id=course.id, title="Quiz", difficulty="beginner")
    db.add(quiz)
    db.flush()
    for idx, q in enumerate(questions):
        db.add(
            QuizQuestion(
                quiz_id=quiz.id,
                question_type=q["question_type"],
                question=q["question"],
                options=q.get("options", []),
                correct_answer=q["correct_answer"],
                order_index=idx,
            )
        )
    db.commit()
    db.refresh(quiz)
    return quiz


def test_is_correct_matching_rules():
    mcq = QuizQuestion(question_type="mcq", question="q", correct_answer="B")
    assert QuizService._is_correct(mcq, "b") is True
    assert QuizService._is_correct(mcq, "c") is False
    assert QuizService._is_correct(mcq, "") is False

    sa = QuizQuestion(question_type="short_answer", question="q", correct_answer="mitochondria")
    assert QuizService._is_correct(sa, "The Mitochondria") is True
    assert QuizService._is_correct(sa, "nucleus") is False


def test_grade_computes_score_and_records_attempt(db, user, make_course):
    course = make_course()
    quiz = _make_quiz(
        db,
        course,
        [
            {"question_type": "mcq", "question": "2+2?", "options": ["3", "4"], "correct_answer": "4"},
            {"question_type": "true_false", "question": "Sky blue?", "correct_answer": "True"},
        ],
    )
    service = QuizService(db)
    q1, q2 = quiz.questions
    submitted = [
        {"question_id": str(q1.id), "answer": "4"},
        {"question_id": str(q2.id), "answer": "False"},
    ]

    result = service.grade(quiz.id, user.id, submitted)

    assert result["attempt"].score == 50.0
    assert result["attempt"].correct_count == 1
    assert result["attempt"].total_questions == 2
    graded = {g["question_id"]: g["is_correct"] for g in result["graded"]}
    assert graded[q1.id] is True
    assert graded[q2.id] is False


def test_grade_unknown_quiz_raises(db, user):
    service = QuizService(db)
    with pytest.raises(NotFoundError):
        service.grade(uuid.uuid4(), user.id, [])


def test_source_material_prefers_upload_text_when_no_chapter(db, user, make_upload, make_course):
    upload = make_upload(extracted_text="Document body text")
    course = make_course(upload=upload)
    service = QuizService(db)

    material = service._source_material(course, None)
    assert material == "Document body text"


@pytest.mark.asyncio
async def test_generate_persists_quiz_from_llm_output(
    db, user, make_upload, make_course, monkeypatch
):
    upload = make_upload(extracted_text="Rich source material about biology.")
    course = make_course(upload=upload)

    async def fake_generate_quiz(material, *, num_questions=5, question_types=None):
        assert "biology" in material
        return {
            "title": "Biology Quiz",
            "description": "desc",
            "questions": [
                {"question_type": "mcq", "question": "Q1?", "options": ["a", "b"], "correct_answer": "a"},
            ],
        }

    monkeypatch.setattr(quiz_service_module, "generate_quiz", fake_generate_quiz)
    service = QuizService(db)

    quiz = await service.generate(user.id, course.id, num_questions=1)

    assert quiz.title == "Biology Quiz"
    assert len(quiz.questions) == 1
    assert quiz.questions[0].question == "Q1?"


@pytest.mark.asyncio
async def test_generate_without_material_raises(db, user, make_upload, make_course):
    upload = make_upload(extracted_text="")
    course = make_course(upload=upload)
    service = QuizService(db)

    with pytest.raises(ValidationAppError):
        await service.generate(user.id, course.id)


@pytest.mark.asyncio
async def test_generate_unknown_course_raises(db, user):
    service = QuizService(db)
    with pytest.raises(NotFoundError):
        await service.generate(user.id, uuid.uuid4())
