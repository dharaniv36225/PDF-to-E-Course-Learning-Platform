"""Robust JSON extraction from LLM output."""
from __future__ import annotations

import json
import re
from typing import Any


def extract_json(text: str) -> Any:
    """Parse JSON from an LLM response, tolerating code fences and surrounding prose."""
    if not text:
        raise ValueError("Empty LLM response")

    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fall back to the first balanced { ... } or [ ... ] block.
    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        start = cleaned.find(open_ch)
        end = cleaned.rfind(close_ch)
        if start != -1 and end != -1 and end > start:
            candidate = cleaned[start : end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
    raise ValueError("Could not parse JSON from LLM response")
