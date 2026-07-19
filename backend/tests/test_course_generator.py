import json

import pytest

import app.ai.course_generator as course_generator
from app.ai.course_generator import _normalize_course, generate_course_structure


def test_normalize_course_fills_defaults():
    result = _normalize_course({}, "advanced")

    assert result["title"] == "Untitled Course"
    assert result["description"] == ""
    assert result["difficulty"] == "advanced"
    assert result["estimated_minutes"] == 0
    assert result["learning_objectives"] == []
    assert result["prerequisites"] == []
    assert result["tags"] == []
    assert result["chapters"] == []


def test_normalize_course_coerces_bad_list_fields():
    data = {"learning_objectives": "not-a-list", "chapters": "nope"}
    result = _normalize_course(data, "beginner")

    assert result["learning_objectives"] == []
    assert result["chapters"] == []


def test_normalize_course_fills_chapter_and_lesson_defaults():
    data = {
        "title": "Course",
        "chapters": [
            {"lessons": [{"title": "L"}, {}]},
        ],
    }
    result = _normalize_course(data, "beginner")

    chapter = result["chapters"][0]
    assert chapter["title"] == "Chapter 1"
    assert chapter["summary"] == ""

    lesson_titled, lesson_default = chapter["lessons"]
    assert lesson_titled["title"] == "L"
    assert lesson_default["title"] == "Lesson 2"
    for lesson in chapter["lessons"]:
        assert lesson["explanation"] == ""
        assert lesson["key_takeaways"] == []
        assert lesson["estimated_minutes"] == 5


class _FakeLLM:
    def __init__(self, payload: str) -> None:
        self.payload = payload
        self.calls: list[dict] = []

    async def complete(self, messages, **kwargs) -> str:
        self.calls.append({"messages": messages, "kwargs": kwargs})
        return self.payload


@pytest.mark.asyncio
async def test_generate_course_structure_normalizes_llm_output(monkeypatch):
    payload = json.dumps({"title": "Intro to AI", "chapters": [{"lessons": [{}]}]})
    fake = _FakeLLM(payload)
    monkeypatch.setattr(course_generator, "get_llm", lambda: fake)

    result = await generate_course_structure("some content", difficulty="beginner", max_chapters=3)

    assert result["title"] == "Intro to AI"
    assert result["chapters"][0]["lessons"][0]["title"] == "Lesson 1"
    # JSON response mode requested from the provider.
    assert fake.calls[0]["kwargs"]["response_json"] is True


@pytest.mark.asyncio
async def test_generate_course_structure_truncates_content(monkeypatch):
    fake = _FakeLLM(json.dumps({"title": "T"}))
    monkeypatch.setattr(course_generator, "get_llm", lambda: fake)

    # Use a marker character absent from the prompt template so the count is exact.
    big_content = "Z" * (course_generator.MAX_CONTENT_CHARS + 5000)
    await generate_course_structure(big_content)

    user_prompt = fake.calls[0]["messages"][1]["content"]
    assert user_prompt.count("Z") == course_generator.MAX_CONTENT_CHARS
