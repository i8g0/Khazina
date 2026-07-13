"""Logging filters that redact sensitive values before records are emitted."""

from __future__ import annotations

import logging
import re

_REDACT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)(password|password_hash)\s*[:=]\s*\S+"), r"\1=***"),
    (
        re.compile(r"(?i)authorization\s*:\s*bearer\s+[A-Za-z0-9\-._~+/]+=*"),
        "authorization: bearer ***",
    ),
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*"), "Bearer ***"),
    (
        re.compile(r"postgresql(?:\+[\w]+)?://[^\s]+"),
        "postgresql://***",
    ),
    (re.compile(r"(?i)(jwt_secret_key|secret_key)\s*[:=]\s*\S+"), r"\1=***"),
)


class SensitiveDataFilter(logging.Filter):
    """Redact secrets and credentials from log message text."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:
            return True
        redacted = message
        for pattern, replacement in _REDACT_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        if redacted != message:
            record.msg = redacted
            record.args = ()
        return True
