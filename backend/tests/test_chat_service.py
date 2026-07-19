"""Integration tests for ChatService (requires the configured database)."""
import uuid

import pytest

import app.services.chat_service as chat_service_module
from app.core.errors import NotFoundError
from app.services.chat_service import ChatService


def test_get_or_create_session_creates_new(db, user, make_course):
    course = make_course()
    service = ChatService(db)

    session = service.get_or_create_session(user.id, course.id, None, "My chat title")

    assert session.id is not None
    assert session.course_id == course.id
    assert session.title == "My chat title"


def test_get_or_create_session_returns_existing(db, user, make_course, make_chat_session):
    course = make_course()
    existing = make_chat_session(course)
    service = ChatService(db)

    fetched = service.get_or_create_session(user.id, course.id, existing.id, "ignored")
    assert fetched.id == existing.id


def test_get_or_create_session_unknown_id_raises(db, user, make_course):
    course = make_course()
    service = ChatService(db)
    with pytest.raises(NotFoundError):
        service.get_or_create_session(user.id, course.id, uuid.uuid4(), "x")


@pytest.mark.asyncio
async def test_answer_persists_user_and_assistant_messages(
    db, user, make_course, make_chat_session, monkeypatch
):
    course = make_course()
    session = make_chat_session(course)
    sources = [{"content": "chunk", "page_number": 2}]

    async def fake_answer(upload_id, question, history):
        assert upload_id == str(course.upload_id)
        return "The answer", sources

    monkeypatch.setattr(chat_service_module.rag, "answer", fake_answer)
    service = ChatService(db)

    message = await service.answer(user.id, course.id, session, "What is X?")

    assert message.role == "assistant"
    assert message.content == "The answer"
    assert message.sources == sources

    history = service._history(session.id)
    assert history[0] == {"role": "user", "content": "What is X?"}
    assert history[1]["role"] == "assistant"


@pytest.mark.asyncio
async def test_answer_unknown_course_raises(db, user, make_course, make_chat_session):
    course = make_course()
    session = make_chat_session(course)
    service = ChatService(db)
    with pytest.raises(NotFoundError):
        await service.answer(user.id, uuid.uuid4(), session, "hi")


def test_delete_session_removes_it(db, user, make_course, make_chat_session):
    course = make_course()
    session = make_chat_session(course)
    service = ChatService(db)

    service.delete_session(session.id, user.id)

    assert service.sessions.get_for_user(session.id, user.id) is None


def test_delete_unknown_session_raises(db, user):
    service = ChatService(db)
    with pytest.raises(NotFoundError):
        service.delete_session(uuid.uuid4(), user.id)
