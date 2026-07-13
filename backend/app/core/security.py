"""Password hashing utilities."""

from __future__ import annotations

import bcrypt


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash suitable for persistence in ``password_hash``."""
    return bcrypt.hashpw(
        plain_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Return whether the plain password matches the stored bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )
