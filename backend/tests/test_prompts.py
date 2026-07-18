from app.ai.prompts import format_context, format_history


def test_format_context_includes_pages():
    chunks = [
        {"content": "Alpha", "page_number": 1},
        {"content": "Beta", "page_number": 3},
    ]
    out = format_context(chunks)
    assert "[p.1]" in out
    assert "[p.3]" in out
    assert "Alpha" in out and "Beta" in out


def test_format_context_empty():
    assert "no relevant context" in format_context([])


def test_format_history_limits():
    messages = [{"role": "user", "content": str(i)} for i in range(10)]
    out = format_history(messages, limit=3)
    assert out.count("User:") == 3
