"""AI course-structure generation."""
from __future__ import annotations

from typing import Any

from app.ai.llm import get_llm
from app.ai.prompts import COURSE_STRUCTURE_TEMPLATE, COURSE_SYSTEM_PROMPT
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Cap prompt content to keep within model context limits.
MAX_CONTENT_CHARS = 24000


async def generate_course_structure(
    content: str,
    *,
    difficulty: str = "beginner",
    max_chapters: int = 8,
) -> dict[str, Any]:
    """Call the LLM to produce a structured course from document text."""
    truncated = content[:MAX_CONTENT_CHARS]
    prompt = COURSE_STRUCTURE_TEMPLATE.format(
        content=truncated,
        difficulty=difficulty,
        max_chapters=max_chapters,
    )
    data = await get_llm().complete_json(
        COURSE_SYSTEM_PROMPT, prompt, temperature=settings.LLM_TEMPERATURE
    )
    return _normalize_course(data, difficulty)


def _normalize_course(data: dict[str, Any], difficulty: str) -> dict[str, Any]:
    data.setdefault("title", "Untitled Course")
    data.setdefault("description", "")
    data.setdefault("difficulty", difficulty)
    data.setdefault("estimated_minutes", 0)
    for key in ("learning_objectives", "prerequisites", "tags"):
        if not isinstance(data.get(key), list):
            data[key] = []
    chapters = data.get("chapters")
    if not isinstance(chapters, list):
        chapters = []
    for c_idx, chapter in enumerate(chapters):
        chapter.setdefault("title", f"Chapter {c_idx + 1}")
        chapter.setdefault("summary", "")
        lessons = chapter.get("lessons")
        if not isinstance(lessons, list):
            lessons = []
        for l_idx, lesson in enumerate(lessons):
            lesson.setdefault("title", f"Lesson {l_idx + 1}")
            for field in ("explanation", "examples", "important_notes", "summary"):
                lesson.setdefault(field, "")
            if not isinstance(lesson.get("key_takeaways"), list):
                lesson["key_takeaways"] = []
            if not isinstance(lesson.get("estimated_minutes"), int):
                lesson["estimated_minutes"] = 5
        chapter["lessons"] = lessons
    data["chapters"] = chapters
    return data
