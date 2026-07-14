"""Add financial_snapshots table for Sprint 6.2 Financial Snapshot (ADR-010).

Revision ID: c3f8a1d92e04
Revises: b7e4a2f91c03
Create Date: 2026-07-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c3f8a1d92e04"
down_revision: Union[str, None] = "b7e4a2f91c03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "financial_snapshots",
        sa.Column("financial_file_id", sa.UUID(), nullable=False),
        sa.Column("import_record_id", sa.UUID(), nullable=True),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("reporting_period_id", sa.UUID(), nullable=True),
        sa.Column("snapshot_version", sa.Integer(), nullable=False),
        sa.Column("parser_version", sa.String(length=50), nullable=False),
        sa.Column("schema_version", sa.String(length=50), nullable=False),
        sa.Column("record_count", sa.Integer(), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "materialized_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "snapshot_version >= 1",
            name="ck_financial_snapshots_version_positive",
        ),
        sa.CheckConstraint(
            "record_count IS NULL OR record_count >= 0",
            name="ck_financial_snapshots_record_count_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["financial_file_id"],
            ["financial_files.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["import_record_id"],
            ["import_records.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["reporting_period_id"],
            ["reporting_periods.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "financial_file_id",
            "snapshot_version",
            name="uq_financial_snapshots_file_version",
        ),
    )
    op.create_index(
        "ix_financial_snapshots_org_created_at",
        "financial_snapshots",
        ["organization_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_financial_snapshots_file_version",
        "financial_snapshots",
        ["financial_file_id", "snapshot_version"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_financial_snapshots_file_version",
        table_name="financial_snapshots",
    )
    op.drop_index(
        "ix_financial_snapshots_org_created_at",
        table_name="financial_snapshots",
    )
    op.drop_table("financial_snapshots")
