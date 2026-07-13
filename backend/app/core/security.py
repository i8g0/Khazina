"""Password hashing utilities (storage only — authentication is a later sprint)."""

from __future__ import annotations

import bcrypt


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash suitable for persistence in ``password_hash``."""
    return bcrypt.hashpw(
        plain_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
