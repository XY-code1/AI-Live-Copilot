"""Tolerant JSON extraction from model output."""

import json


def parse_json_object(text: str) -> dict:
    """Parse the first balanced JSON object found in text.

    Models sometimes wrap JSON in prose or markdown fences; a greedy regex
    breaks when more than one brace group is present.
    """
    candidates = [index for index, char in enumerate(text) if char == "{"]
    for start in candidates:
        decoder = json.JSONDecoder()
        try:
            payload, _ = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    raise ValueError("未找到有效的 JSON 对象")
