"""Tests for upload PDF validation (magic bytes, MIME, size, corruption)."""
from __future__ import annotations

import fitz  # PyMuPDF
import pytest

from app.core.errors import ValidationAppError
from app.utils.pdf import validate_pdf

MAX_BYTES = 25 * 1024 * 1024


def _valid_pdf_bytes(text: str = "Hello, world.") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def _kwargs(**overrides):
    base = {
        "content_type": "application/pdf",
        "filename": "document.pdf",
        "max_bytes": MAX_BYTES,
    }
    base.update(overrides)
    return base


def test_valid_pdf_passes():
    validate_pdf(_valid_pdf_bytes(), **_kwargs())


def test_valid_pdf_with_generic_octet_stream_content_type():
    validate_pdf(_valid_pdf_bytes(), **_kwargs(content_type="application/octet-stream"))


def test_rejects_non_pdf_extension():
    with pytest.raises(ValidationAppError, match="PDF"):
        validate_pdf(_valid_pdf_bytes(), **_kwargs(filename="notes.txt"))


def test_rejects_disallowed_content_type():
    with pytest.raises(ValidationAppError, match="content type"):
        validate_pdf(_valid_pdf_bytes(), **_kwargs(content_type="text/plain"))


def test_rejects_empty_file():
    with pytest.raises(ValidationAppError, match="empty"):
        validate_pdf(b"", **_kwargs())


def test_rejects_oversized_file():
    with pytest.raises(ValidationAppError, match="limit"):
        validate_pdf(_valid_pdf_bytes(), **_kwargs(max_bytes=64))


def test_rejects_missing_magic_bytes():
    with pytest.raises(ValidationAppError, match="valid PDF"):
        validate_pdf(b"GIF89a" + b"\x00" * 100, **_kwargs())


def test_rejects_corrupted_pdf_with_valid_header():
    # Correct magic bytes but not a parseable document.
    corrupted = b"%PDF-1.4\n" + b"\xde\xad\xbe\xef" * 64
    with pytest.raises(ValidationAppError, match="corrupted|malformed|no pages"):
        validate_pdf(corrupted, **_kwargs())


def test_tolerates_leading_whitespace_before_header():
    validate_pdf(b"\r\n " + _valid_pdf_bytes(), **_kwargs())
