"""Regression: prompt templates must not contain mixed Arabic-Latin tokens."""

from __future__ import annotations

import re

import pytest

from app.ai.prompts.languages import get_language_pack, supported_languages

_MIXED_TOKEN = re.compile(r"[\u0600-\u06FFa-zA-Z]+")


def _mixed_script_tokens(text: str) -> list[str]:
    found: list[str] = []
    for token in _MIXED_TOKEN.findall(text):
        has_ar = bool(re.search(r"[\u0621-\u064A]", token))
        has_lat = bool(re.search(r"[A-Za-z]", token))
        if has_ar and has_lat:
            found.append(token)
    return found


def _iter_language_pack_strings() -> list[tuple[str, str]]:
    strings: list[tuple[str, str]] = []
    for code in supported_languages():
        pack = get_language_pack(code)
        strings.append((f"{code}:system_prompt", pack.system_prompt))
        strings.append((f"{code}:output_rules", pack.output_rules))
        strings.append((f"{code}:facts_header", pack.facts_header))
        strings.append((f"{code}:no_facts_message", pack.no_facts_message))
        for task, template in pack.task_templates.items():
            strings.append((f"{code}:{task.value}", template))
    return strings


def test_prompts_no_mixed_script_tokens() -> None:
    violations: list[str] = []
    for label, text in _iter_language_pack_strings():
        tokens = _mixed_script_tokens(text)
        if tokens:
            violations.append(f"{label}: {tokens[:5]}")
    assert not violations, "Mixed-script tokens found:\n" + "\n".join(violations)
