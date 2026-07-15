"""Event fingerprint idempotency tests."""

from __future__ import annotations

import uuid

from app.notifications.fingerprint import compute_event_fingerprint


def test_fingerprint_is_deterministic() -> None:
    kwargs = {
        "platform_event_kind": "analysis_completed",
        "source_entity_type": "analysis_run",
        "source_entity_id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
        "recipient_user_id": uuid.UUID("22222222-2222-2222-2222-222222222222"),
        "source_marker": "completed:2026-07-15T10:00:00+00:00",
    }
    assert compute_event_fingerprint(**kwargs) == compute_event_fingerprint(**kwargs)


def test_fingerprint_differs_for_recipient() -> None:
    base = {
        "platform_event_kind": "analysis_completed",
        "source_entity_type": "analysis_run",
        "source_entity_id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
        "source_marker": "completed:2026-07-15T10:00:00+00:00",
    }
    user_a = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    user_b = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    assert compute_event_fingerprint(
        recipient_user_id=user_a, **base
    ) != compute_event_fingerprint(recipient_user_id=user_b, **base)
