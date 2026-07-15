"""Deterministic event fingerprinting for idempotent materialization."""

from __future__ import annotations

import hashlib
import uuid


def compute_event_fingerprint(
    *,
    platform_event_kind: str,
    source_entity_type: str,
    source_entity_id: uuid.UUID,
    recipient_user_id: uuid.UUID,
    source_marker: str,
) -> str:
    """Stable fingerprint per platform event, source, recipient, and status marker."""
    payload = (
        f"{platform_event_kind}|{source_entity_type}|{source_entity_id}|"
        f"{recipient_user_id}|{source_marker}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
