"""Add report_exports and user_notification_preferences for Sprint 6.9.

Revision ID: b9d4e7f16a21
Revises: a8c3e6f05d10
Create Date: 2026-07-15 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b9d4e7f16a21"
down_revision: Union[str, None] = "a8c3e6f05d10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "report_exports",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("report_id", sa.UUID(), nullable=False),
        sa.Column("export_format", sa.String(length=16), nullable=False),
        sa.Column("content_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("preferences_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("export_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("storage_reference", sa.String(length=1024), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["report_id"], ["reports.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "report_id",
            "export_format",
            "content_fingerprint",
            "preferences_fingerprint",
            name="uq_report_exports_dedup",
        ),
    )
    op.create_index(
        "ix_report_exports_report_id",
        "report_exports",
        ["report_id"],
    )

    op.create_table(
        "user_notification_preferences",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "preferences_document",
            sa.dialects.postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_user_notification_preferences_org_user",
        ),
    )


def downgrade() -> None:
    op.drop_table("user_notification_preferences")
    op.drop_index("ix_report_exports_report_id", table_name="report_exports")
    op.drop_table("report_exports")
