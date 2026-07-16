"""Risk analysis SQLAlchemy model metadata tests."""

from __future__ import annotations

from app.db.models import RiskAnalysisResult, RiskCategory, RiskFinding


def test_risk_category_table_name() -> None:
    assert RiskCategory.__tablename__ == "risk_categories"


def test_risk_analysis_result_unique_run_constraint() -> None:
    names = {
        constraint.name
        for constraint in RiskAnalysisResult.__table__.constraints
        if constraint.name
    }
    assert "uq_risk_analysis_results_analysis_run_id" in names


def test_risk_finding_score_check_constraint() -> None:
    names = {
        constraint.name
        for constraint in RiskFinding.__table__.constraints
        if constraint.name
    }
    assert "ck_risk_findings_score_range" in names
    assert "ck_risk_findings_status" in names


def test_analysis_run_risk_relationships() -> None:
    from app.db.models.analysis import AnalysisRun

    assert "risk_analysis_result" in AnalysisRun.__mapper__.relationships
    assert "risk_findings" in AnalysisRun.__mapper__.relationships
