import pytest

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


def test_extract_object_ignores_trailing_prose():
    text = 'Sure! {"title": "T", "items": [1, 2]} Hope that helps.'
    assert extract_json(text) == {"title": "T", "items": [1, 2]}


def test_empty_response_raises():
    with pytest.raises(ValueError, match="Empty"):
        extract_json("")


def test_unparseable_response_raises():
    with pytest.raises(ValueError, match="Could not parse"):
        extract_json("there is definitely no json here")
