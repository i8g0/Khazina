"""Add content_representation to reports for Sprint 6.6 Report Content Representation.

Revision ID: e6c1a4f93b08
Revises: d4a9b2e81f05
Create Date: 2026-07-15 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "e6c1a4f93b08"
down_revision: Union[str, None] = "d4a9b2e81f05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "reports",
        sa.Column(
            "content_representation",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("reports", "content_representation")
