"""Normalization guards for AI-generated course structures."""
from app.ai.course_generator import _normalize_course


def test_normalize_course_handles_non_dict_payload():
    for bad in ([1, 2], None, "not json", 7):
        result = _normalize_course(bad, "beginner")
        assert result["title"] == "Untitled Course"
        assert result["difficulty"] == "beginner"
        assert result["chapters"] == []
        assert result["learning_objectives"] == []


def test_normalize_course_skips_non_dict_chapters_and_lessons():
    raw = {
        "title": "T",
        "chapters": [
            "a stray string chapter",
            {
                "title": "Ch 1",
                "lessons": ["stray lesson", {"title": "L1"}],
            },
        ],
    }
    result = _normalize_course(raw, "beginner")
    assert len(result["chapters"]) == 1
    chapter = result["chapters"][0]
    assert chapter["title"] == "Ch 1"
    assert len(chapter["lessons"]) == 1
    lesson = chapter["lessons"][0]
    assert lesson["title"] == "L1"
    assert lesson["estimated_minutes"] == 5
    assert lesson["key_takeaways"] == []


def test_normalize_course_defaults_missing_titles():
    raw = {"chapters": [{"lessons": [{}]}]}
    result = _normalize_course(raw, "advanced")
    assert result["chapters"][0]["title"] == "Chapter 1"
    assert result["chapters"][0]["lessons"][0]["title"] == "Lesson 1"
