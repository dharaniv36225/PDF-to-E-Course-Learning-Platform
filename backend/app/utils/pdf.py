"""PDF validation and text extraction using PyMuPDF (fitz)."""
from __future__ import annotations

from app.core.errors import ValidationAppError
from app.core.logging import get_logger

logger = get_logger(__name__)

PDF_MAGIC = b"%PDF-"

# Content types browsers/clients legitimately send for PDF uploads. Some clients
# omit a precise type and fall back to a generic binary type, so that is tolerated
# here — the magic-byte and structural checks below are the authoritative guard.
ALLOWED_PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
    "application/acrobat",
    "application/vnd.pdf",
    "text/pdf",
    "text/x-pdf",
    "application/octet-stream",
}


def validate_pdf(
    data: bytes,
    *,
    content_type: str | None,
    filename: str | None,
    max_bytes: int,
) -> None:
    """Validate an uploaded PDF, raising ``ValidationAppError`` on any problem.

    Checks, in order: file extension, declared MIME type, non-empty, size limit,
    ``%PDF-`` magic bytes and structural readability (rejects corrupted, encrypted
    or empty documents).
    """
    if not filename or not filename.lower().endswith(".pdf"):
        raise ValidationAppError("Only PDF files are supported (a '.pdf' extension is required).")

    if content_type:
        normalized = content_type.split(";", 1)[0].strip().lower()
        if normalized and normalized not in ALLOWED_PDF_CONTENT_TYPES:
            raise ValidationAppError(
                f"Unsupported content type '{content_type}'. Expected a PDF (application/pdf)."
            )

    if not data:
        raise ValidationAppError("The uploaded file is empty.")

    max_mb = max(1, max_bytes // (1024 * 1024))
    if len(data) > max_bytes:
        raise ValidationAppError(f"File exceeds the {max_mb}MB upload limit.")

    # Some tools prepend a BOM or whitespace before the header; tolerate that.
    header = data[:1024].lstrip(b"\x00\r\n\t\x0c ")
    if not header.startswith(PDF_MAGIC):
        raise ValidationAppError("File is not a valid PDF (missing '%PDF-' header).")

    ensure_readable_pdf(data)


def ensure_readable_pdf(data: bytes) -> None:
    """Open the document to confirm it is a structurally valid, usable PDF."""
    import fitz  # PyMuPDF

    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception as exc:  # noqa: BLE001
        raise ValidationAppError(
            f"The PDF appears to be corrupted or malformed: {exc}"
        ) from exc

    with doc:
        if doc.needs_pass:
            raise ValidationAppError("Password-protected PDFs are not supported.")
        if doc.page_count < 1:
            raise ValidationAppError("The PDF contains no pages.")


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
