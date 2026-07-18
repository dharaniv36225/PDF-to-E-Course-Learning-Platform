"""Text chunking utilities using LangChain's recursive splitter."""
from __future__ import annotations

from app.core.config import settings


def split_pages(pages: list[dict]) -> list[dict]:
    """Split page dicts ({page_number, text}) into overlapping chunks.

    Returns a list of {content, chunk_index, page_number}.
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[dict] = []
    index = 0
    for page in pages:
        text = (page.get("text") or "").strip()
        if not text:
            continue
        for piece in splitter.split_text(text):
            piece = piece.strip()
            if not piece:
                continue
            chunks.append(
                {
                    "content": piece,
                    "chunk_index": index,
                    "page_number": page.get("page_number"),
                }
            )
            index += 1
    return chunks
