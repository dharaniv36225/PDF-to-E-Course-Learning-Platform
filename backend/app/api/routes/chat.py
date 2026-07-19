"""RAG chatbot routes with streaming support."""
from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatMessageRead,
    ChatRequest,
    ChatResponse,
    ChatSessionDetail,
    ChatSessionRead,
)
from app.schemas.common import Message
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    """Non-streaming chat completion answering strictly from the document."""
    service = ChatService(db)
    session = service.get_or_create_session(
        current_user.id, payload.course_id, payload.session_id, payload.message
    )
    message = await service.answer(current_user.id, payload.course_id, session, payload.message)
    return ChatResponse(session_id=session.id, message=ChatMessageRead.model_validate(message))


@router.post("/stream")
async def chat_stream(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Server-Sent Events streaming chat endpoint."""
    service = ChatService(db)
    session = service.get_or_create_session(
        current_user.id, payload.course_id, payload.session_id, payload.message
    )
    iterator, sources, finalize = await service.stream(
        current_user.id, payload.course_id, session, payload.message
    )

    async def event_generator() -> AsyncIterator[str]:
        yield _sse({"type": "session", "session_id": str(session.id)})
        yield _sse({"type": "sources", "sources": sources})
        collected: list[str] = []
        async for token in iterator:
            collected.append(token)
            yield _sse({"type": "token", "content": token})
        full_text = "".join(collected)
        message = finalize(full_text)
        yield _sse({"type": "done", "message_id": str(message.id)})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


@router.get("/sessions", response_model=list[ChatSessionRead])
def list_sessions(
    course_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatSessionRead]:
    return [
        ChatSessionRead.model_validate(session)
        for session in ChatService(db).list_sessions(current_user.id, course_id)
    ]


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSessionDetail:
    return ChatSessionDetail.model_validate(
        ChatService(db).get_session_detail(session_id, current_user.id)
    )


@router.delete("/sessions/{session_id}", response_model=Message)
def delete_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Message:
    ChatService(db).delete_session(session_id, current_user.id)
    return Message(message="Chat session deleted")
