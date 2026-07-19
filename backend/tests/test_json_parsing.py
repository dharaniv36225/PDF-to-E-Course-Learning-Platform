from app.utils.json_parsing import extract_json


def test_extract_plain_json():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_fenced_json():
    text = "Here is the result:\n```json\n{\"x\": [1, 2]}\n```\nThanks!"
    assert extract_json(text) == {"x": [1, 2]}


def test_extract_embedded_object():
    text = "prefix {\"k\": \"v\"} suffix"
    assert extract_json(text) == {"k": "v"}


def test_extract_array():
    assert extract_json("[1, 2, 3]") == [1, 2, 3]


def test_extract_invalid_raises_with_cause():
    import pytest

    with pytest.raises(ValueError) as exc_info:
        extract_json("not json at all")
    assert exc_info.value.__cause__ is not None
