"""Add risk analysis persistence tables (Sprint 9.3).

Revision ID: e8a1c4f03d21
Revises: d2f6b8a14e37
Create Date: 2026-07-16 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "e8a1c4f03d21"
down_revision: Union[str, None] = "d2f6b8a14e37"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RISK_CATEGORIES_SEED: tuple[dict[str, object], ...] = (
    {
        "code": "financial",
        "label_ar": "مخاطر مالية",
        "label_en": "Financial",
        "description": "Core financial statement stress and waste exposure",
        "is_active": True,
        "sort_order": 1,
    },
    {
        "code": "liquidity",
        "label_ar": "مخاطر السيولة",
        "label_en": "Liquidity",
        "description": "Cash runway and short-term payment capacity",
        "is_active": True,
        "sort_order": 2,
    },
    {
        "code": "operational",
        "label_ar": "مخاطر تشغيلية",
        "label_en": "Operational",
        "description": "Operational control and process execution risk",
        "is_active": True,
        "sort_order": 3,
    },
    {
        "code": "compliance",
        "label_ar": "مخاطر امتثال",
        "label_en": "Compliance",
        "description": "Governance and regulatory monitoring thresholds",
        "is_active": True,
        "sort_order": 4,
    },
    {
        "code": "vendor",
        "label_ar": "مخاطر الموردين",
        "label_en": "Vendor",
        "description": "Supplier concentration and third-party dependency",
        "is_active": True,
        "sort_order": 5,
    },
    {
        "code": "fraud",
        "label_ar": "مخاطر احتيال",
        "label_en": "Fraud",
        "description": "Deterministic spend anomaly flags",
        "is_active": True,
        "sort_order": 6,
    },
    {
        "code": "strategic",
        "label_ar": "مخاطر استراتيجية",
        "label_en": "Strategic",
        "description": "Strategic plan and scenario alignment",
        "is_active": True,
        "sort_order": 7,
    },
    {
        "code": "budget",
        "label_ar": "مخاطر الموازنة",
        "label_en": "Budget",
        "description": "Budget versus actual variance",
        "is_active": True,
        "sort_order": 8,
    },
    {
        "code": "forecast",
        "label_ar": "مخاطر التوقعات",
        "label_en": "Forecast",
        "description": "Forward-looking projection reliability",
        "is_active": True,
        "sort_order": 9,
    },
)


def upgrade() -> None:
    op.create_table(
        "risk_categories",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("label_ar", sa.String(length=100), nullable=False),
        sa.Column("label_en", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("sort_order", sa.SmallInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("code"),
    )
    op.create_index(
        "ix_risk_categories_active_sort",
        "risk_categories",
        ["is_active", "sort_order"],
    )

    op.create_table(
        "risk_analysis_results",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("analysis_run_id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("total_findings", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("high_priority_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("medium_priority_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("low_priority_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("overall_posture_level", sa.String(length=30), nullable=False),
        sa.Column("top_category_code", sa.String(length=50), nullable=True),
        sa.Column("facts_contract_version", sa.String(length=20), nullable=False),
        sa.Column("source_snapshot_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["analysis_run_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["source_snapshot_id"], ["financial_snapshots.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["top_category_code"], ["risk_categories.code"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("analysis_run_id", name="uq_risk_analysis_results_analysis_run_id"),
    )
    op.create_index(
        "ix_risk_analysis_results_org_created",
        "risk_analysis_results",
        ["organization_id", "created_at"],
    )

    op.create_table(
        "risk_findings",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("analysis_run_id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("category_code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("likelihood", sa.String(length=50), nullable=False),
        sa.Column("impact", sa.String(length=50), nullable=False),
        sa.Column("score", sa.SmallInteger(), nullable=False),
        sa.Column("priority", sa.String(length=50), nullable=False),
        sa.Column("detection_rule_id", sa.String(length=100), nullable=False),
        sa.Column(
            "evidence",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "finding_status",
            sa.String(length=30),
            server_default="detected",
            nullable=False,
        ),
        sa.Column("promoted_risk_id", sa.UUID(), nullable=True),
        sa.Column("department_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("score >= 0 AND score <= 100", name="ck_risk_findings_score_range"),
        sa.CheckConstraint(
            "finding_status IN ('detected', 'reviewed', 'promoted', 'dismissed')",
            name="ck_risk_findings_status",
        ),
        sa.ForeignKeyConstraint(["analysis_run_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["category_code"], ["risk_categories.code"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["promoted_risk_id"], ["risks.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_risk_findings_run_priority",
        "risk_findings",
        ["analysis_run_id", "priority"],
    )
    op.create_index(
        "ix_risk_findings_org_status_priority",
        "risk_findings",
        ["organization_id", "finding_status", "priority"],
    )
    op.create_index(
        "ix_risk_findings_promoted_risk_id",
        "risk_findings",
        ["promoted_risk_id"],
    )

    op.bulk_insert(
        sa.table(
            "risk_categories",
            sa.column("code", sa.String),
            sa.column("label_ar", sa.String),
            sa.column("label_en", sa.String),
            sa.column("description", sa.Text),
            sa.column("is_active", sa.Boolean),
            sa.column("sort_order", sa.SmallInteger),
        ),
        list(RISK_CATEGORIES_SEED),
    )


def downgrade() -> None:
    op.drop_index("ix_risk_findings_promoted_risk_id", table_name="risk_findings")
    op.drop_index("ix_risk_findings_org_status_priority", table_name="risk_findings")
    op.drop_index("ix_risk_findings_run_priority", table_name="risk_findings")
    op.drop_table("risk_findings")
    op.drop_index("ix_risk_analysis_results_org_created", table_name="risk_analysis_results")
    op.drop_table("risk_analysis_results")
    op.drop_index("ix_risk_categories_active_sort", table_name="risk_categories")
    op.drop_table("risk_categories")
