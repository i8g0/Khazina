"""Enterprise risk register model metadata tests."""

from __future__ import annotations

from app.db.models import Risk, RiskEvent


def test_risk_lifecycle_constraint_exists() -> None:
    names = {
        constraint.name for constraint in Risk.__table__.constraints if constraint.name
    }
    assert "ck_risks_lifecycle_status" in names
    assert "ck_risks_source_type" in names


def test_risk_provenance_columns() -> None:
    column_names = {column.name for column in Risk.__table__.columns}
    assert "source_finding_id" in column_names
    assert "source_analysis_run_id" in column_names
    assert "source_snapshot_id" in column_names
    assert "lifecycle_status" in column_names


def test_risk_event_table() -> None:
    assert RiskEvent.__tablename__ == "risk_events"
