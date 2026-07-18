"""Retrieval-Augmented Generation pipeline for the document chatbot."""
from __future__ import annotations

from collections.abc import AsyncIterator

from app.ai.llm import get_llm
from app.ai.prompts import (
    RAG_SYSTEM_PROMPT,
    RAG_USER_TEMPLATE,
    format_context,
    format_history,
)
from app.ai.vector_store import get_vector_store
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def retrieve(upload_id: str, question: str, top_k: int | None = None) -> list[dict]:
    """Retrieve the most relevant chunks for a question."""
    store = get_vector_store()
    return store.query(upload_id, question, top_k or settings.RETRIEVER_TOP_K)


def _build_messages(question: str, chunks: list[dict], history: list[dict]) -> list[dict]:
    user_content = RAG_USER_TEMPLATE.format(
        context=format_context(chunks),
        history=format_history(history),
        question=question,
    )
    return [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


async def answer(
    upload_id: str,
    question: str,
    history: list[dict],
) -> tuple[str, list[dict]]:
    """Return a full answer plus the source chunks used."""
    chunks = retrieve(upload_id, question)
    messages = _build_messages(question, chunks, history)
    llm = get_llm()
    text = await llm.complete(messages)
    return text, chunks


async def stream_answer(
    upload_id: str,
    question: str,
    history: list[dict],
) -> tuple[AsyncIterator[str], list[dict]]:
    """Return an async token iterator plus the source chunks used."""
    chunks = retrieve(upload_id, question)
    messages = _build_messages(question, chunks, history)
    llm = get_llm()
    return llm.stream(messages), chunks


async def summarize(text: str, instruction: str = "Summarize the following content.") -> str:
    """Generic summarization helper used for chapter/document summaries."""
    llm = get_llm()
    return await llm.complete(
        [
            {"role": "system", "content": "You are a concise, accurate summarizer."},
            {"role": "user", "content": f"{instruction}\n\n{text[:16000]}"},
        ]
    )
