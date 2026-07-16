"""Enterprise risk register governance (Sprint 9.4).

Revision ID: f9c2d7a31b44
Revises: e8a1c4f03d21
Create Date: 2026-07-16 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "f9c2d7a31b44"
down_revision: Union[str, None] = "e8a1c4f03d21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "risks",
        sa.Column(
            "lifecycle_status",
            sa.String(length=50),
            server_default="accepted",
            nullable=False,
        ),
    )
    op.add_column(
        "risks",
        sa.Column("category_code", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "risks",
        sa.Column("source_type", sa.String(length=30), nullable=True),
    )
    op.add_column(
        "risks",
        sa.Column("source_analysis_run_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "risks",
        sa.Column("source_finding_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "risks",
        sa.Column("source_snapshot_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "risks",
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_foreign_key(
        "fk_risks_category_code",
        "risks",
        "risk_categories",
        ["category_code"],
        ["code"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_risks_source_analysis_run_id",
        "risks",
        "analysis_runs",
        ["source_analysis_run_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_risks_source_finding_id",
        "risks",
        "risk_findings",
        ["source_finding_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_risks_source_snapshot_id",
        "risks",
        "financial_snapshots",
        ["source_snapshot_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index(
        "ix_risks_org_category_status",
        "risks",
        ["organization_id", "category_code", "status"],
    )
    op.create_index(
        "ix_risks_org_lifecycle",
        "risks",
        ["organization_id", "lifecycle_status"],
    )
    op.create_index("ix_risks_source_finding_id", "risks", ["source_finding_id"])

    op.create_check_constraint(
        "ck_risks_source_type",
        "risks",
        "source_type IS NULL OR source_type IN ('manual', 'engine', 'import')",
    )
    op.create_check_constraint(
        "ck_risks_lifecycle_status",
        "risks",
        "lifecycle_status IN ('accepted', 'monitoring', 'mitigated', 'resolved', 'archived')",
    )

    op.execute(
        sa.text(
            "UPDATE risks SET lifecycle_status = 'monitoring' WHERE status = 'in_progress'"
        )
    )
    op.execute(
        sa.text(
            "UPDATE risks SET lifecycle_status = 'archived' WHERE status = 'closed'"
        )
    )

    op.create_table(
        "risk_events",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("risk_id", sa.UUID(), nullable=True),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("from_status", sa.String(length=50), nullable=True),
        sa.Column("to_status", sa.String(length=50), nullable=True),
        sa.Column("actor_user_id", sa.UUID(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["risk_id"], ["risks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_risk_events_risk_created",
        "risk_events",
        ["risk_id", "created_at"],
    )
    op.create_index(
        "ix_risk_events_org_type_created",
        "risk_events",
        ["organization_id", "event_type", "created_at"],
    )

    op.drop_constraint("ck_risk_findings_status", "risk_findings", type_="check")
    op.create_check_constraint(
        "ck_risk_findings_status",
        "risk_findings",
        "finding_status IN ('detected', 'under_review', 'reviewed', 'promoted', 'dismissed')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_risk_findings_status", "risk_findings", type_="check")
    op.create_check_constraint(
        "ck_risk_findings_status",
        "risk_findings",
        "finding_status IN ('detected', 'reviewed', 'promoted', 'dismissed')",
    )

    op.drop_index("ix_risk_events_org_type_created", table_name="risk_events")
    op.drop_index("ix_risk_events_risk_created", table_name="risk_events")
    op.drop_table("risk_events")

    op.drop_constraint("ck_risks_lifecycle_status", "risks", type_="check")
    op.drop_constraint("ck_risks_source_type", "risks", type_="check")
    op.drop_index("ix_risks_source_finding_id", table_name="risks")
    op.drop_index("ix_risks_org_lifecycle", table_name="risks")
    op.drop_index("ix_risks_org_category_status", table_name="risks")
    op.drop_constraint("fk_risks_source_snapshot_id", "risks", type_="foreignkey")
    op.drop_constraint("fk_risks_source_finding_id", "risks", type_="foreignkey")
    op.drop_constraint("fk_risks_source_analysis_run_id", "risks", type_="foreignkey")
    op.drop_constraint("fk_risks_category_code", "risks", type_="foreignkey")
    op.drop_column("risks", "detected_at")
    op.drop_column("risks", "source_snapshot_id")
    op.drop_column("risks", "source_finding_id")
    op.drop_column("risks", "source_analysis_run_id")
    op.drop_column("risks", "source_type")
    op.drop_column("risks", "category_code")
    op.drop_column("risks", "lifecycle_status")
