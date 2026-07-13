"""Deterministic LLM response parsing."""

from __future__ import annotations

import json
import re
from typing import Any

from app.ai.exceptions import ResponseParseError
from app.ai.parsers.types import ParsedResponse

_JSON_FENCE_PATTERN = re.compile(
    r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```",
    re.DOTALL | re.IGNORECASE,
)


class ResponseParser:
    """Parse JSON or plain-text LLM responses into typed objects."""

    def parse(self, raw_response: str) -> ParsedResponse:
        text = raw_response.strip()
        if not text:
            raise ResponseParseError("LLM response is empty")

        json_payload = self._try_parse_json(text)
        if json_payload is not None:
            return self._build_json_response(text, json_payload)

        fenced = _JSON_FENCE_PATTERN.search(text)
        if fenced is not None:
            json_payload = self._try_parse_json(fenced.group(1).strip())
            if json_payload is not None:
                return self._build_json_response(text, json_payload)

        return ParsedResponse(format="text", text=text, data=None)

    @staticmethod
    def _try_parse_json(text: str) -> dict[str, Any] | list[Any] | None:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return None
        if isinstance(payload, (dict, list)):
            return payload
        raise ResponseParseError("JSON root must be an object or array")

    @staticmethod
    def _build_json_response(
        raw_text: str,
        payload: dict[str, Any] | list[Any],
    ) -> ParsedResponse:
        if isinstance(payload, dict):
            text = str(payload.get("content") or payload.get("summary") or raw_text)
        else:
            text = raw_text
        return ParsedResponse(format="json", text=text, data=payload)
