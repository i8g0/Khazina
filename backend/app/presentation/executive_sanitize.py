"""Executive presentation sanitizer — strips technical identifiers from user-facing text."""

from __future__ import annotations

import re

# Dot-notation internal keys (waste.top_category, risk.score_max, …)
_DOT_NOTATION_KEY = re.compile(
    r"\b(?:waste|risk|scenario)\.[a-z0-9_.]+\b",
    re.IGNORECASE,
)

# Standalone snake_case tokens (facts_contract_version, source_snapshot_id, …)
_SNAKE_CASE_TOKEN = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")

# UUIDs
_UUID = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)

_REFERENCE_FACTS_HEADER = re.compile(
    r"^\s*الحقائق\s*المرجعية\s*:?\s*",
    re.MULTILINE | re.IGNORECASE,
)

_ACTION_PREFIX = re.compile(r"^الإجراء\s*المقتر[ح]?\s*:\s*", re.UNICODE)
_RATIONALE_PREFIX = re.compile(r"^المبرر\s*:\s*", re.UNICODE)
_CATEGORY_PREFIX = re.compile(r"^الفئة\s*:\s*.+\n?", re.MULTILINE)

_FORBIDDEN_LITERALS: tuple[str, ...] = (
    "facts_contract",
    "facts_contract_version",
    "metadata",
    "engine_id",
    "engine_version",
    "tasks_executed",
    "source_snapshot_id",
    "source_context",
    "prompt_version",
    "parsed_format",
    "traceability",
    "category_breakdowns",
    "vendor_findings",
    "json",
    "uuid",
    "null",
    "undefined",
)

from app.presentation.business_labels import localize_category_tokens

_WHITESPACE = re.compile(r"\n{3,}")
_MULTI_SPACE = re.compile(r" {2,}")


def sanitize_executive_text(text: str) -> str:
    """Remove technical leakage from text shown to executives."""
    if not text or not text.strip():
        return text

    cleaned = text.strip()

    # Drop reference-facts blocks entirely
    cleaned = _strip_reference_facts_blocks(cleaned)

    # Remove dot-notation keys
    cleaned = _DOT_NOTATION_KEY.sub("", cleaned)

    # Remove forbidden literal substrings (case-insensitive)
    for literal in _FORBIDDEN_LITERALS:
        cleaned = re.sub(re.escape(literal), "", cleaned, flags=re.IGNORECASE)

    # Remove UUIDs
    cleaned = _UUID.sub("", cleaned)

    # Remove remaining snake_case tokens that look like code identifiers
    cleaned = _SNAKE_CASE_TOKEN.sub("", cleaned)

    cleaned = _MULTI_SPACE.sub(" ", cleaned)
    cleaned = _WHITESPACE.sub("\n\n", cleaned)
    cleaned = localize_category_tokens(cleaned)
    return cleaned.strip()


def extract_recommendation_executive_text(body: str) -> tuple[str, str]:
    """
    Extract executive-facing title (action) and description (rationale only).
    Strips الحقائق المرجعية and technical labels.
    """
    raw = body.strip()
    if not raw:
        return "", ""

    action = ""
    rationale = ""

    action_match = re.search(
        r"الإجراء\s*المقتر[ح]?\s*:\s*(.+?)(?=\n\s*المبرر\s*:|$)",
        raw,
        re.DOTALL | re.UNICODE,
    )
    if action_match:
        action = action_match.group(1).strip()
    else:
        first_line = raw.split("\n", 1)[0].strip()
        action = _ACTION_PREFIX.sub("", first_line).strip()

    rationale_match = re.search(
        r"المبرر\s*:\s*(.+?)(?=\n\s*الحقائق\s*المرج|$)",
        raw,
        re.DOTALL | re.UNICODE,
    )
    if rationale_match:
        rationale = rationale_match.group(1).strip()
    elif action and action in raw:
        remainder = raw.split(action, 1)[-1].strip()
        remainder = _RATIONALE_PREFIX.sub("", remainder).strip()
        remainder = _strip_reference_facts_blocks(remainder)
        rationale = remainder

    action = sanitize_executive_text(_ACTION_PREFIX.sub("", action))
    rationale = sanitize_executive_text(_RATIONALE_PREFIX.sub("", rationale))

    if not rationale:
        rationale = action
    if not action:
        action = rationale[:120] if rationale else raw[:120]

    return action, rationale


def _strip_reference_facts_blocks(text: str) -> str:
    """Remove blocks starting with الحقائق المرجعية through end of paragraph."""
    lines: list[str] = []
    skip_block = False
    for line in text.splitlines():
        if _REFERENCE_FACTS_HEADER.match(line) or line.strip().startswith("الحقائق المرجعية"):
            skip_block = True
            continue
        if skip_block:
            if re.match(r"^\s*(المبرر|الإجراء|القرار|\d+\.)\s*", line):
                skip_block = False
            else:
                continue
        lines.append(line)
    return "\n".join(lines)


def contains_technical_leakage(text: str) -> bool:
    """Return True if text still contains forbidden technical patterns."""
    if not text:
        return False
    if _DOT_NOTATION_KEY.search(text):
        return True
    lowered = text.lower()
    return any(lit in lowered for lit in _FORBIDDEN_LITERALS)
