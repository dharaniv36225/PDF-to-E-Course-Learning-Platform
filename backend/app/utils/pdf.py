"""PDF text extraction using PyMuPDF (fitz)."""
from __future__ import annotations

from app.core.errors import ValidationAppError
from app.core.logging import get_logger

logger = get_logger(__name__)


def extract_pages(file_bytes: bytes) -> tuple[list[dict], int]:
    """Extract text per page from PDF bytes.

    Returns (pages, page_count) where each page is {page_number, text}.
    """
    import fitz  # PyMuPDF

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:  # noqa: BLE001
        raise ValidationAppError(f"Unable to read PDF: {exc}") from exc

    pages: list[dict] = []
    with doc:
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            text = page.get_text("text") or ""
            pages.append({"page_number": page_index + 1, "text": text})
        page_count = doc.page_count

    if not any(p["text"].strip() for p in pages):
        logger.warning("PDF contained no extractable text (possibly scanned)")
    return pages, page_count


def pages_to_text(pages: list[dict]) -> str:
    """Concatenate page texts into a single string."""
    return "\n\n".join(p["text"] for p in pages if p.get("text"))
