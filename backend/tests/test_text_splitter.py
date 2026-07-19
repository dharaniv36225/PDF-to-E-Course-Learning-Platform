from app.ai.text_splitter import split_pages


def test_split_pages_produces_indexed_chunks():
    pages = [
        {"page_number": 1, "text": "First page content."},
        {"page_number": 2, "text": "Second page content."},
    ]
    chunks = split_pages(pages)

    assert len(chunks) == 2
    assert [c["chunk_index"] for c in chunks] == [0, 1]
    assert [c["page_number"] for c in chunks] == [1, 2]
    assert all(c["content"] for c in chunks)


def test_split_pages_skips_blank_pages():
    pages = [
        {"page_number": 1, "text": "   "},
        {"page_number": 2, "text": ""},
        {"page_number": 3, "text": None},
        {"page_number": 4, "text": "Real text"},
    ]
    chunks = split_pages(pages)

    assert len(chunks) == 1
    assert chunks[0]["page_number"] == 4
    assert chunks[0]["chunk_index"] == 0


def test_split_pages_splits_long_text_into_multiple_chunks():
    long_text = "\n\n".join(f"Paragraph number {i} with some words." for i in range(200))
    chunks = split_pages([{"page_number": 1, "text": long_text}])

    assert len(chunks) > 1
    # Indices are contiguous and start at zero.
    assert [c["chunk_index"] for c in chunks] == list(range(len(chunks)))


def test_split_pages_empty_input():
    assert split_pages([]) == []
