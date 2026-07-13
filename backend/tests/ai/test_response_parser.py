"""Response Parser unit tests."""

from __future__ import annotations

import pytest

from app.ai.exceptions import ResponseParseError
from app.ai.parsers.response_parser import ResponseParser


def test_response_parser_parses_json_object() -> None:
    parsed = ResponseParser().parse('{"summary": "ok", "content": "executive text"}')
    assert parsed.format == "json"
    assert parsed.text == "executive text"
    assert parsed.data == {"summary": "ok", "content": "executive text"}


def test_response_parser_parses_fenced_json() -> None:
    raw = 'Here is the result:\n```json\n{"content": "fenced"}\n```'
    parsed = ResponseParser().parse(raw)
    assert parsed.format == "json"
    assert parsed.data == {"content": "fenced"}


def test_response_parser_falls_back_to_text() -> None:
    parsed = ResponseParser().parse("Plain narrative response.")
    assert parsed.format == "text"
    assert parsed.data is None
    assert parsed.text == "Plain narrative response."


def test_response_parser_empty_response_raises() -> None:
    with pytest.raises(ResponseParseError):
        ResponseParser().parse("   ")
