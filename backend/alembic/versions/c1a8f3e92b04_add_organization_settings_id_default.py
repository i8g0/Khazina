"""Add server default for organization_settings.id.

Revision ID: c1a8f3e92b04
Revises: b9d4e7f16a21
Create Date: 2026-07-15 11:10:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "c1a8f3e92b04"
down_revision: Union[str, None] = "b9d4e7f16a21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE organization_settings "
        "ALTER COLUMN id SET DEFAULT gen_random_uuid()"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE organization_settings "
        "ALTER COLUMN id DROP DEFAULT"
    )
