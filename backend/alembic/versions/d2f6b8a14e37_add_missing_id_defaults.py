"""Add server defaults for id columns missing gen_random_uuid().

Revision ID: d2f6b8a14e37
Revises: c1a8f3e92b04
Create Date: 2026-07-15 14:20:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "d2f6b8a14e37"
down_revision: Union[str, None] = "c1a8f3e92b04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLES = (
    "notifications",
    "notification_read_receipts",
    "report_exports",
    "user_notification_preferences",
)


def upgrade() -> None:
    for table in _TABLES:
        op.execute(
            f"ALTER TABLE {table} "
            "ALTER COLUMN id SET DEFAULT gen_random_uuid()"
        )


def downgrade() -> None:
    for table in reversed(_TABLES):
        op.execute(f"ALTER TABLE {table} ALTER COLUMN id DROP DEFAULT")
