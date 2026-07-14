"""Add source_snapshot_id to analysis_runs for Sprint 6.3 snapshot provenance.

Revision ID: d4a9b2e81f05
Revises: c3f8a1d92e04
Create Date: 2026-07-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4a9b2e81f05"
down_revision: Union[str, None] = "c3f8a1d92e04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "analysis_runs",
        sa.Column("source_snapshot_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_analysis_runs_source_snapshot_id",
        "analysis_runs",
        "financial_snapshots",
        ["source_snapshot_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_analysis_runs_source_snapshot_id",
        "analysis_runs",
        ["source_snapshot_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_analysis_runs_source_snapshot_id", table_name="analysis_runs")
    op.drop_constraint(
        "fk_analysis_runs_source_snapshot_id",
        "analysis_runs",
        type_="foreignkey",
    )
    op.drop_column("analysis_runs", "source_snapshot_id")
