"""Safe composition hooks — notification failures never roll back domain work."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from typing import TypeVar

from app.notifications.builder import NotificationBuilder

logger = logging.getLogger(__name__)

T = TypeVar("T")


def try_materialize(
    builder: NotificationBuilder | None,
    initiating_user_id: uuid.UUID | None,
    materialize: Callable[[], T | None],
) -> T | None:
    if builder is None or initiating_user_id is None:
        return None
    try:
        return materialize()
    except Exception:
        logger.exception("Notification materialization failed")
        return None
