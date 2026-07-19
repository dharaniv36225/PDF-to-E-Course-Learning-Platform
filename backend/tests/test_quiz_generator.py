from app.ai.quiz_generator import _normalize_quiz


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


def test_normalize_quiz_handles_non_dict_payload():
    """A malformed LLM response (list/None/str) must not raise."""
    for bad in ([1, 2, 3], None, "not json", 42):
        result = _normalize_quiz(bad, ["mcq"])
        assert result["title"] == "Quiz"
        assert result["questions"] == []


def test_normalize_quiz_skips_non_dict_and_nonstring_fields():
    raw = {
        "questions": [
            "totally not a question object",
            {"question_type": "mcq", "question": 123, "options": [1, 2], "correct_answer": 4},
        ]
    }
    result = _normalize_quiz(raw, ["mcq"])
    assert len(result["questions"]) == 1
    q = result["questions"][0]
    assert q["question"] == "123"
    assert q["options"] == ["1", "2"]
    assert q["correct_answer"] == "4"
