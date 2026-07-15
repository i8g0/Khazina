"""Notification domain exceptions."""

from __future__ import annotations


class NotificationError(Exception):
    """Base notification error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
