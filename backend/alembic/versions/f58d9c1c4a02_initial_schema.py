"""Initial schema — creates all 25 tables of the approved Khazina MVP schema.

Generated via Alembic autogeneration from the Sprint 3.3 SQLAlchemy models
(app.db.models) and manually reviewed against docs/DATABASE_SCHEMA_DESIGN.md.
Includes primary keys, foreign keys (with RESTRICT/CASCADE/SET NULL rules),
unique constraints, check constraints, B-tree and partial indexes, and
server-side defaults (gen_random_uuid(), now(), business defaults).

Revision ID: f58d9c1c4a02
Revises:
Create Date: 2026-07-12 13:25:18.666194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f58d9c1c4a02'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('organizations',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('platform_name', sa.String(length=100), server_default='خزينة', nullable=False),
    sa.Column('executive_title', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('departments',
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('name_ar', sa.String(length=100), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=True),
    sa.Column('display_order', sa.SmallInteger(), server_default=sa.text('0'), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'name_ar', name='uq_departments_org_name_ar')
    )
    op.create_table('reporting_periods',
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('label', sa.String(length=100), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('end_date IS NULL OR start_date IS NULL OR end_date >= start_date', name='ck_reporting_periods_valid_date_range'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('uq_reporting_periods_one_active_per_org', 'reporting_periods', ['organization_id'], unique=True, postgresql_where=sa.text('is_active IS TRUE'))
    op.create_table('simulation_scenarios',
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=300), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=50), server_default='draft', nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_simulation_scenarios_org_status', 'simulation_scenarios', ['organization_id', 'status'], unique=False)
    op.create_table('data_quality_snapshots',
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('reporting_period_id', sa.UUID(), nullable=True),
    sa.Column('overall_score', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('evaluated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['reporting_period_id'], ['reporting_periods.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('financial_files',
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('department_id', sa.UUID(), nullable=True),
    sa.Column('reporting_period_id', sa.UUID(), nullable=True),
    sa.Column('file_name', sa.String(length=500), nullable=False),
    sa.Column('storage_path', sa.String(length=1000), nullable=True),
    sa.Column('size_bytes', sa.BigInteger(), nullable=True),
    sa.Column('size_display', sa.String(length=50), nullable=True),
    sa.Column('mime_type', sa.String(length=100), nullable=True),
    sa.Column('processing_status', sa.String(length=50), server_default='pending', nullable=False),
    sa.Column('upload_source', sa.String(length=50), server_default='repository', nullable=False),
    sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('size_bytes IS NULL OR size_bytes >= 0', name='ck_financial_files_size_bytes_non_negative'),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['reporting_period_id'], ['reporting_periods.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_financial_files_org_status', 'financial_files', ['organization_id', 'processing_status'], unique=False)
    op.create_index('ix_financial_files_org_uploaded_at', 'financial_files', ['organization_id', 'uploaded_at'], unique=False)
    op.create_table('risks',
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('department_id', sa.UUID(), nullable=True),
    sa.Column('reporting_period_id', sa.UUID(), nullable=True),
    sa.Column('name', sa.String(length=300), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('priority', sa.String(length=50), nullable=False),
    sa.Column('score', sa.SmallInteger(), nullable=False),
    sa.Column('status', sa.String(length=50), server_default='active', nullable=False),
    sa.Column('owner_label', sa.String(length=200), nullable=True),
    sa.Column('likelihood', sa.String(length=50), nullable=True),
    sa.Column('impact', sa.String(length=50), nullable=True),
    sa.Column('category_label', sa.String(length=100), nullable=True),
    sa.Column('last_updated_at', sa.Date(), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('score >= 0 AND score <= 100', name='ck_risks_score_range'),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['reporting_period_id'], ['reporting_periods.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_risks_org_department', 'risks', ['organization_id', 'department_id'], unique=False)
    op.create_index('ix_risks_org_status_priority', 'risks', ['organization_id', 'status', 'priority'], unique=False)
    op.create_table('simulation_assumptions',
    sa.Column('scenario_id', sa.UUID(), nullable=False),
    sa.Column('label', sa.String(length=200), nullable=False),
    sa.Column('value', sa.String(length=500), nullable=False),
    sa.Column('display_order', sa.SmallInteger(), server_default=sa.text('0'), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['scenario_id'], ['simulation_scenarios.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('timeline_events',
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('reporting_period_id', sa.UUID(), nullable=True),
    sa.Column('event_date', sa.Date(), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('event_type', sa.String(length=50), nullable=False),
    sa.Column('related_entity_type', sa.String(length=50), nullable=True),
    sa.Column('related_entity_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['reporting_period_id'], ['reporting_periods.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_timeline_events_org_event_date', 'timeline_events', ['organization_id', 'event_date'], unique=False)
    op.create_table('waste_trend_points',
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('reporting_period_id', sa.UUID(), nullable=True),
    sa.Column('month_label', sa.String(length=50), nullable=False),
    sa.Column('month_order', sa.SmallInteger(), nullable=False),
    sa.Column('waste_amount', sa.Numeric(precision=18, scale=2), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['reporting_period_id'], ['reporting_periods.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'reporting_period_id', 'month_label', name='uq_waste_trend_points_org_period_month')
    )
    op.create_table('analysis_runs',
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('reporting_period_id', sa.UUID(), nullable=True),
    sa.Column('source_file_id', sa.UUID(), nullable=True),
    sa.Column('analysis_type', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('status', sa.String(length=50), server_default='pending', nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('runtime_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['reporting_period_id'], ['reporting_periods.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['source_file_id'], ['financial_files.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_analysis_runs_org_completed_at', 'analysis_runs', ['organization_id', 'completed_at'], unique=False)
    op.create_index('ix_analysis_runs_org_type_status', 'analysis_runs', ['organization_id', 'analysis_type', 'status'], unique=False)
    op.create_index('ix_analysis_runs_source_file_id', 'analysis_runs', ['source_file_id'], unique=False)
    op.create_table('data_quality_checks',
    sa.Column('snapshot_id', sa.UUID(), nullable=False),
    sa.Column('check_name', sa.String(length=200), nullable=False),
    sa.Column('result_percent', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('details', sa.Text(), nullable=True),
    sa.Column('display_order', sa.SmallInteger(), server_default=sa.text('0'), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['snapshot_id'], ['data_quality_snapshots.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('import_records',
    sa.Column('financial_file_id', sa.UUID(), nullable=False),
    sa.Column('imported_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('record_count', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status <> 'failed' OR error_message IS NOT NULL", name='ck_import_records_failed_requires_error_message'),
    sa.CheckConstraint('record_count IS NULL OR record_count >= 0', name='ck_import_records_record_count_non_negative'),
    sa.ForeignKeyConstraint(['financial_file_id'], ['financial_files.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_import_records_file_imported_at', 'import_records', ['financial_file_id', 'imported_at'], unique=False)
    op.create_table('risk_mitigation_plans',
    sa.Column('risk_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=300), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('target_date', sa.Date(), nullable=False),
    sa.Column('owner_label', sa.String(length=200), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['risk_id'], ['risks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reports',
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('department_id', sa.UUID(), nullable=True),
    sa.Column('reporting_period_id', sa.UUID(), nullable=True),
    sa.Column('source_file_id', sa.UUID(), nullable=True),
    sa.Column('analysis_run_id', sa.UUID(), nullable=True),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('report_type', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=50), server_default='draft', nullable=False),
    sa.Column('summary', sa.Text(), nullable=False),
    sa.Column('published_at', sa.Date(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['analysis_run_id'], ['analysis_runs.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['reporting_period_id'], ['reporting_periods.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['source_file_id'], ['financial_files.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reports_org_published_at', 'reports', ['organization_id', 'published_at'], unique=False)
    op.create_index('ix_reports_org_type_status', 'reports', ['organization_id', 'report_type', 'status'], unique=False)
    op.create_table('simulation_runs',
    sa.Column('scenario_id', sa.UUID(), nullable=False),
    sa.Column('analysis_run_id', sa.UUID(), nullable=False),
    sa.Column('result_title', sa.String(length=300), nullable=True),
    sa.Column('result_description', sa.Text(), nullable=True),
    sa.Column('confidence_label', sa.String(length=20), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['analysis_run_id'], ['analysis_runs.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['scenario_id'], ['simulation_scenarios.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('analysis_run_id', name='uq_simulation_runs_analysis_run_id')
    )
    op.create_index('ix_simulation_runs_scenario_id', 'simulation_runs', ['scenario_id'], unique=False)
    op.create_table('waste_analysis_results',
    sa.Column('analysis_run_id', sa.UUID(), nullable=False),
    sa.Column('total_waste_amount', sa.Numeric(precision=18, scale=2), nullable=False),
    sa.Column('waste_percentage', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('top_category_name', sa.String(length=200), nullable=True),
    sa.Column('top_category_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('potential_savings_amount', sa.Numeric(precision=18, scale=2), nullable=True),
    sa.Column('active_savings_opportunities', sa.SmallInteger(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('waste_percentage >= 0 AND waste_percentage <= 100', name='ck_waste_analysis_results_waste_percentage_range'),
    sa.ForeignKeyConstraint(['analysis_run_id'], ['analysis_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('analysis_run_id', name='uq_waste_analysis_results_analysis_run_id')
    )
    op.create_table('waste_category_breakdowns',
    sa.Column('analysis_run_id', sa.UUID(), nullable=False),
    sa.Column('department_id', sa.UUID(), nullable=True),
    sa.Column('category_name', sa.String(length=200), nullable=False),
    sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
    sa.Column('percentage', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('display_order', sa.SmallInteger(), server_default=sa.text('0'), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['analysis_run_id'], ['analysis_runs.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_waste_category_breakdowns_run_department', 'waste_category_breakdowns', ['analysis_run_id', 'department_id'], unique=False)
    op.create_table('waste_vendor_findings',
    sa.Column('analysis_run_id', sa.UUID(), nullable=False),
    sa.Column('vendor_name', sa.String(length=300), nullable=False),
    sa.Column('category_label', sa.String(length=100), nullable=True),
    sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
    sa.Column('deviation_label', sa.String(length=20), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['analysis_run_id'], ['analysis_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('recommendations',
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('domain_source', sa.String(length=50), nullable=False),
    sa.Column('external_ref', sa.String(length=50), nullable=True),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('priority', sa.String(length=50), nullable=False),
    sa.Column('confidence_label', sa.String(length=20), nullable=True),
    sa.Column('estimated_savings_amount', sa.Numeric(precision=18, scale=2), nullable=True),
    sa.Column('department_id', sa.UUID(), nullable=True),
    sa.Column('analysis_run_id', sa.UUID(), nullable=True),
    sa.Column('risk_id', sa.UUID(), nullable=True),
    sa.Column('simulation_run_id', sa.UUID(), nullable=True),
    sa.Column('is_dashboard_featured', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('source_context', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('num_nonnulls(analysis_run_id, risk_id, simulation_run_id) <= 1', name='ck_recommendations_at_most_one_source_fk'),
    sa.ForeignKeyConstraint(['analysis_run_id'], ['analysis_runs.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['risk_id'], ['risks.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['simulation_run_id'], ['simulation_runs.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_recommendations_dashboard_featured', 'recommendations', ['organization_id'], unique=False, postgresql_where=sa.text('is_dashboard_featured IS TRUE'))
    op.create_index('ix_recommendations_org_domain_priority', 'recommendations', ['organization_id', 'domain_source', 'priority'], unique=False)
    op.create_table('simulation_action_items',
    sa.Column('simulation_run_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=300), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=50), server_default='proposed', nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['simulation_run_id'], ['simulation_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('simulation_chart_points',
    sa.Column('simulation_run_id', sa.UUID(), nullable=False),
    sa.Column('quarter_label', sa.String(length=50), nullable=False),
    sa.Column('quarter_order', sa.SmallInteger(), nullable=False),
    sa.Column('baseline_amount', sa.Numeric(precision=18, scale=2), nullable=False),
    sa.Column('projected_amount', sa.Numeric(precision=18, scale=2), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['simulation_run_id'], ['simulation_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('simulation_comparison_metrics',
    sa.Column('simulation_run_id', sa.UUID(), nullable=False),
    sa.Column('metric_name', sa.String(length=200), nullable=False),
    sa.Column('current_value', sa.String(length=100), nullable=False),
    sa.Column('simulated_value', sa.String(length=100), nullable=False),
    sa.Column('change_value', sa.String(length=100), nullable=False),
    sa.Column('direction', sa.String(length=20), nullable=False),
    sa.Column('display_order', sa.SmallInteger(), server_default=sa.text('0'), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['simulation_run_id'], ['simulation_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('simulation_forecast_summaries',
    sa.Column('simulation_run_id', sa.UUID(), nullable=False),
    sa.Column('baseline_label', sa.String(length=100), nullable=False),
    sa.Column('baseline_value', sa.String(length=100), nullable=False),
    sa.Column('projected_label', sa.String(length=100), nullable=False),
    sa.Column('projected_value', sa.String(length=100), nullable=False),
    sa.Column('delta_label', sa.String(length=100), nullable=False),
    sa.Column('delta_value', sa.String(length=100), nullable=False),
    sa.Column('confidence_label', sa.String(length=20), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['simulation_run_id'], ['simulation_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('simulation_run_id', name='uq_simulation_forecast_summaries_simulation_run_id')
    )
    op.create_table('simulation_impact_items',
    sa.Column('simulation_run_id', sa.UUID(), nullable=False),
    sa.Column('category_label', sa.String(length=200), nullable=False),
    sa.Column('baseline_value', sa.String(length=100), nullable=False),
    sa.Column('projected_value', sa.String(length=100), nullable=False),
    sa.Column('change_value', sa.String(length=100), nullable=False),
    sa.Column('direction', sa.String(length=20), nullable=False),
    sa.Column('display_order', sa.SmallInteger(), server_default=sa.text('0'), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['simulation_run_id'], ['simulation_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('simulation_impact_items')
    op.drop_table('simulation_forecast_summaries')
    op.drop_table('simulation_comparison_metrics')
    op.drop_table('simulation_chart_points')
    op.drop_table('simulation_action_items')
    op.drop_index('ix_recommendations_org_domain_priority', table_name='recommendations')
    op.drop_index('ix_recommendations_dashboard_featured', table_name='recommendations', postgresql_where=sa.text('is_dashboard_featured IS TRUE'))
    op.drop_table('recommendations')
    op.drop_table('waste_vendor_findings')
    op.drop_index('ix_waste_category_breakdowns_run_department', table_name='waste_category_breakdowns')
    op.drop_table('waste_category_breakdowns')
    op.drop_table('waste_analysis_results')
    op.drop_index('ix_simulation_runs_scenario_id', table_name='simulation_runs')
    op.drop_table('simulation_runs')
    op.drop_index('ix_reports_org_type_status', table_name='reports')
    op.drop_index('ix_reports_org_published_at', table_name='reports')
    op.drop_table('reports')
    op.drop_table('risk_mitigation_plans')
    op.drop_index('ix_import_records_file_imported_at', table_name='import_records')
    op.drop_table('import_records')
    op.drop_table('data_quality_checks')
    op.drop_index('ix_analysis_runs_source_file_id', table_name='analysis_runs')
    op.drop_index('ix_analysis_runs_org_type_status', table_name='analysis_runs')
    op.drop_index('ix_analysis_runs_org_completed_at', table_name='analysis_runs')
    op.drop_table('analysis_runs')
    op.drop_table('waste_trend_points')
    op.drop_index('ix_timeline_events_org_event_date', table_name='timeline_events')
    op.drop_table('timeline_events')
    op.drop_table('simulation_assumptions')
    op.drop_index('ix_risks_org_status_priority', table_name='risks')
    op.drop_index('ix_risks_org_department', table_name='risks')
    op.drop_table('risks')
    op.drop_index('ix_financial_files_org_uploaded_at', table_name='financial_files')
    op.drop_index('ix_financial_files_org_status', table_name='financial_files')
    op.drop_table('financial_files')
    op.drop_table('data_quality_snapshots')
    op.drop_index('ix_simulation_scenarios_org_status', table_name='simulation_scenarios')
    op.drop_table('simulation_scenarios')
    op.drop_index('uq_reporting_periods_one_active_per_org', table_name='reporting_periods', postgresql_where=sa.text('is_active IS TRUE'))
    op.drop_table('reporting_periods')
    op.drop_table('departments')
    op.drop_table('organizations')
