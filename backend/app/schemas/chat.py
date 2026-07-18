"""Chat schemas."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class Source(BaseModel):
    content: str
    page_number: int | None = None
    chunk_index: int | None = None
    score: float | None = None


class ChatMessageRead(ORMModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    sources: list[Source] | None = None
    created_at: datetime


class ChatSessionRead(ORMModel):
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    created_at: datetime


class ChatSessionDetail(ChatSessionRead):
    messages: list[ChatMessageRead] = []


class ChatRequest(BaseModel):
    course_id: uuid.UUID
    session_id: uuid.UUID | None = None
    message: str = Field(min_length=1)
    stream: bool = True


class ChatResponse(BaseModel):
    session_id: uuid.UUID
    message: ChatMessageRead
