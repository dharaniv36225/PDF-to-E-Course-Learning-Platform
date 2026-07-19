"""Tests for the chat SSE streaming error-handling path."""
from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.db.session import get_db
from app.main import app
from app.services import chat_service


class _FakeSession:
    id = uuid.uuid4()


class _FakeUser:
    id = uuid.uuid4()


def _parse_sse(body: str) -> list[dict]:
    events = []
    for block in body.strip().split("\n\n"):
        line = block.strip()
        if line.startswith("data:"):
            events.append(json.loads(line[len("data:") :].strip()))
    return events


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    app.dependency_overrides[get_current_user] = lambda: _FakeUser()
    app.dependency_overrides[get_db] = lambda: iter([object()])

    def _get_or_create_session(self, *args, **kwargs):
        return _FakeSession()

    monkeypatch.setattr(chat_service.ChatService, "__init__", lambda self, db: None)
    monkeypatch.setattr(
        chat_service.ChatService, "get_or_create_session", _get_or_create_session
    )
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_stream_emits_error_event_when_llm_fails(client, monkeypatch):
    async def _failing_stream(self, *args, **kwargs):
        async def _iterator() -> AsyncIterator[str]:
            yield "partial"
            raise RuntimeError("provider exploded")

        return _iterator(), [], lambda text: None

    monkeypatch.setattr(chat_service.ChatService, "stream", _failing_stream)

    with client.stream(
        "POST",
        "/api/v1/chat/stream",
        json={"course_id": str(uuid.uuid4()), "message": "hi"},
    ) as resp:
        assert resp.status_code == 200
        events = _parse_sse(resp.read().decode())

    types = [e["type"] for e in events]
    assert "error" in types
    assert "done" not in types
    error_event = next(e for e in events if e["type"] == "error")
    assert error_event["message"]


def test_stream_completes_with_done_event(client, monkeypatch):
    finalized = _FakeSession()

    async def _ok_stream(self, *args, **kwargs):
        async def _iterator() -> AsyncIterator[str]:
            yield "hello "
            yield "world"

        return _iterator(), [], lambda text: finalized

    monkeypatch.setattr(chat_service.ChatService, "stream", _ok_stream)

    with client.stream(
        "POST",
        "/api/v1/chat/stream",
        json={"course_id": str(uuid.uuid4()), "message": "hi"},
    ) as resp:
        assert resp.status_code == 200
        events = _parse_sse(resp.read().decode())

    types = [e["type"] for e in events]
    assert types[-1] == "done"
    assert "".join(e["content"] for e in events if e["type"] == "token") == "hello world"
