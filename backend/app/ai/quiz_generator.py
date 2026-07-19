"""AI quiz generation."""
from __future__ import annotations

from typing import Any

from app.ai.llm import get_llm
from app.ai.prompts import QUIZ_SYSTEM_PROMPT, QUIZ_TEMPLATE
from app.core.logging import get_logger
from app.utils.json_parsing import extract_json

logger = get_logger(__name__)

MAX_CONTENT_CHARS = 16000
VALID_TYPES = {"mcq", "true_false", "short_answer"}


async def generate_quiz(
    content: str,
    *,
    num_questions: int = 5,
    question_types: list[str] | None = None,
) -> dict[str, Any]:
    """Generate a quiz from the provided material."""
    types = [t for t in (question_types or list(VALID_TYPES)) if t in VALID_TYPES]
    if not types:
        types = ["mcq"]
    prompt = QUIZ_TEMPLATE.format(
        content=content[:MAX_CONTENT_CHARS],
        num_questions=num_questions,
        question_types=", ".join(types),
    )
    llm = get_llm()
    raw = await llm.complete(
        [
            {"role": "system", "content": QUIZ_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_json=True,
    )
    data = extract_json(raw)
    return _normalize_quiz(data, types)


def _normalize_quiz(data: Any, types: list[str]) -> dict[str, Any]:
    if not isinstance(data, dict):
        logger.warning("LLM quiz payload was not a JSON object (got %s); using defaults", type(data).__name__)
        data = {}
    data.setdefault("title", "Quiz")
    data.setdefault("description", "")
    questions = data.get("questions")
    if not isinstance(questions, list):
        questions = []
    normalized: list[dict] = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        q_type = q.get("question_type") if q.get("question_type") in VALID_TYPES else types[0]
        raw_options = q.get("options") if isinstance(q.get("options"), list) else []
        options = [str(opt) for opt in raw_options]
        if q_type == "true_false":
            options = ["True", "False"]
        elif q_type == "short_answer":
            options = []
        normalized.append(
            {
                "question_type": q_type,
                "question": str(q.get("question", "")).strip(),
                "options": options,
                "correct_answer": str(q.get("correct_answer", "")).strip(),
                "explanation": str(q.get("explanation") or "").strip(),
            }
        )
    data["questions"] = [q for q in normalized if q["question"] and q["correct_answer"]]
    return data
