import json

import pytest

import app.ai.quiz_generator as quiz_generator
from app.ai.quiz_generator import _normalize_quiz, generate_quiz


def test_normalize_quiz_fixes_options():
    raw = {
        "title": "T",
        "questions": [
            {"question_type": "true_false", "question": "Sky is blue?", "correct_answer": "True"},
            {
                "question_type": "mcq",
                "question": "2+2?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4",
                "explanation": "basic math",
            },
            {"question_type": "short_answer", "question": "Define AI", "correct_answer": "artificial intelligence"},
        ],
    }
    result = _normalize_quiz(raw, ["mcq", "true_false", "short_answer"])
    tf, mcq, sa = result["questions"]
    assert tf["options"] == ["True", "False"]
    assert mcq["options"] == ["3", "4", "5", "6"]
    assert sa["options"] == []


def test_normalize_quiz_drops_incomplete():
    raw = {"questions": [{"question_type": "mcq", "question": "", "correct_answer": ""}]}
    result = _normalize_quiz(raw, ["mcq"])
    assert result["questions"] == []


def test_normalize_quiz_defaults_invalid_type_to_first():
    raw = {"questions": [{"question_type": "essay", "question": "Q?", "correct_answer": "A"}]}
    result = _normalize_quiz(raw, ["short_answer"])
    assert result["questions"][0]["question_type"] == "short_answer"


class _FakeLLM:
    def __init__(self, payload: str) -> None:
        self.payload = payload
        self.calls: list[dict] = []

    async def complete(self, messages, **kwargs) -> str:
        self.calls.append({"messages": messages, "kwargs": kwargs})
        return self.payload


@pytest.mark.asyncio
async def test_generate_quiz_filters_invalid_types(monkeypatch):
    payload = json.dumps(
        {
            "title": "Q",
            "questions": [
                {"question_type": "mcq", "question": "2+2?", "options": ["3", "4"], "correct_answer": "4"}
            ],
        }
    )
    fake = _FakeLLM(payload)
    monkeypatch.setattr(quiz_generator, "get_llm", lambda: fake)

    result = await generate_quiz("material", num_questions=1, question_types=["essay", "mcq"])

    assert result["questions"][0]["correct_answer"] == "4"
    prompt = fake.calls[0]["messages"][1]["content"]
    assert "mcq" in prompt
    assert "essay" not in prompt


@pytest.mark.asyncio
async def test_generate_quiz_defaults_to_mcq_when_no_valid_types(monkeypatch):
    fake = _FakeLLM(json.dumps({"questions": []}))
    monkeypatch.setattr(quiz_generator, "get_llm", lambda: fake)

    await generate_quiz("material", question_types=["nonsense"])

    prompt = fake.calls[0]["messages"][1]["content"]
    assert "mcq" in prompt
