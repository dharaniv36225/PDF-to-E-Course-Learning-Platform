import fitz  # PyMuPDF
import pytest

from app.core.errors import ValidationAppError
from app.utils.pdf import extract_pages, pages_to_text


def _make_pdf(page_texts: list[str]) -> bytes:
    doc = fitz.open()
    for text in page_texts:
        page = doc.new_page()
        if text:
            page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def test_extract_pages_reads_text_and_count():
    data = _make_pdf(["Hello world", "Second page"])
    pages, count = extract_pages(data)

    assert count == 2
    assert [p["page_number"] for p in pages] == [1, 2]
    assert "Hello world" in pages[0]["text"]
    assert "Second page" in pages[1]["text"]


def test_extract_pages_handles_pages_without_text():
    data = _make_pdf(["", ""])
    pages, count = extract_pages(data)

    assert count == 2
    assert all(p["text"].strip() == "" for p in pages)


def test_extract_pages_invalid_bytes_raises():
    with pytest.raises(ValidationAppError):
        extract_pages(b"not a pdf at all")


def test_pages_to_text_concatenates_non_empty():
    pages = [
        {"page_number": 1, "text": "alpha"},
        {"page_number": 2, "text": ""},
        {"page_number": 3, "text": "beta"},
    ]
    assert pages_to_text(pages) == "alpha\n\nbeta"


def test_pages_to_text_empty():
    assert pages_to_text([]) == ""
