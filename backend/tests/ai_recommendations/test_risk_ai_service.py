"""Risk AI recommendation service tests."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app.ai.prompts.tasks import PromptTask
from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.pipeline import AiTaskPipeline
from app.ai_recommendations.risk_constants import RISK_TASK_EXECUTION_ORDER
from app.ai_recommendations.service import AiRecommendationService
from app.db.models.enums import AnalysisRunStatus, AnalysisType, RecommendationDomain
from app.services.exceptions import InvalidStateError, ResourceNotFoundError
from tests.ai_recommendations.risk_conftest import (
    MockRiskOllamaByTask,
    sample_risk_runtime_metadata,
)


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def run_id() -> uuid.UUID:
    return uuid.uuid4()


def _completed_risk_run(
    org_id: uuid.UUID, run_id: uuid.UUID, snapshot_id: uuid.UUID
) -> MagicMock:
    run = MagicMock()
    run.id = run_id
    run.organization_id = org_id
    run.source_snapshot_id = snapshot_id
    run.source_file_id = uuid.uuid4()
    run.analysis_type = AnalysisType.RISK
    run.status = AnalysisRunStatus.COMPLETED
    run.runtime_metadata = sample_risk_runtime_metadata()
    return run


def _risk_service(
    run: MagicMock,
    *,
    mock_ollama: MockRiskOllamaByTask | None = None,
    risk_result: MagicMock | None = None,
) -> AiRecommendationService:
    session = MagicMock()
    analysis_repo = MagicMock()
    waste_repo = MagicMock()
    risk_analysis_repo = MagicMock()
    recommendation_repo = MagicMock()

    analysis_repo.get.return_value = run
    analysis_repo.update.side_effect = lambda r, values: setattr(
        r, "runtime_metadata", values["runtime_metadata"]
    ) or r
    risk_analysis_repo.get_result_for_run.return_value = risk_result or MagicMock(
        id=uuid.uuid4(), source_snapshot_id=run.source_snapshot_id
    )
    risk_analysis_repo.list_findings.return_value = []
    recommendation_repo.list_for_analysis_run.return_value = []
    recommendation_repo.create.side_effect = lambda rec: rec

    pipeline = AiTaskPipeline(
        ollama_client=mock_ollama or MockRiskOllamaByTask(),
        ollama_model="test-model",
        prompt_language="ar",
    )
    return AiRecommendationService(
        session,
        analysis_repo,
        waste_repo,
        recommendation_repo,
        risk_analysis_repository=risk_analysis_repo,
        task_pipeline=pipeline,
    )


def test_generate_risk_ai_success(
    org_id: uuid.UUID, run_id: uuid.UUID
) -> None:
    snapshot_id = uuid.uuid4()
    run = _completed_risk_run(org_id, run_id, snapshot_id)
    service = _risk_service(run)
    outcome = service.generate_risk_recommendations(org_id, run_id)

    assert outcome.ai_insights["domain"] == "risk"
    assert outcome.ai_insights["risk_executive_summary"]
    assert outcome.ai_insights["risk_explanation"]
    assert outcome.ai_insights["traceability"]["analysis_run_id"] == str(run_id)
    assert len(outcome.recommendations) == 5
    assert outcome.recommendations[0].domain_source == RecommendationDomain.RISK


def test_generate_risk_ai_rejects_non_risk_run(
    org_id: uuid.UUID, run_id: uuid.UUID
) -> None:
    run = _completed_risk_run(org_id, run_id, uuid.uuid4())
    run.analysis_type = AnalysisType.FINANCIAL_WASTE
    service = _risk_service(run)
    with pytest.raises(InvalidStateError):
        service.generate_risk_recommendations(org_id, run_id)


def test_generate_risk_ai_requires_gold_result(
    org_id: uuid.UUID, run_id: uuid.UUID
) -> None:
    run = _completed_risk_run(org_id, run_id, uuid.uuid4())
    service = _risk_service(run, risk_result=None)
    service._risk_analysis.get_result_for_run.return_value = None
    with pytest.raises(InvalidStateError):
        service.generate_risk_recommendations(org_id, run_id)


def test_generate_risk_ai_idempotency_guard(
    org_id: uuid.UUID, run_id: uuid.UUID
) -> None:
    run = _completed_risk_run(org_id, run_id, uuid.uuid4())
    run.runtime_metadata["ai_insights"] = {"domain": "risk", "generated_at": "x"}
    service = _risk_service(run)
    with pytest.raises(AiRecommendationError) as exc:
        service.generate_risk_recommendations(org_id, run_id)
    assert exc.value.error_code == "ai_insights_already_exist"


def test_risk_pipeline_executes_tasks_in_order(
    org_id: uuid.UUID, run_id: uuid.UUID
) -> None:
    mock = MockRiskOllamaByTask()
    run = _completed_risk_run(org_id, run_id, uuid.uuid4())
    service = _risk_service(run, mock_ollama=mock)
    service.generate_risk_recommendations(org_id, run_id)
    assert mock.calls[: len(RISK_TASK_EXECUTION_ORDER)] == list(
        RISK_TASK_EXECUTION_ORDER
    )


def test_missing_run_raises_not_found(org_id: uuid.UUID, run_id: uuid.UUID) -> None:
    session = MagicMock()
    analysis_repo = MagicMock()
    analysis_repo.get.return_value = None
    service = AiRecommendationService(
        session,
        analysis_repo,
        MagicMock(),
        MagicMock(),
        risk_analysis_repository=MagicMock(),
        task_pipeline=AiTaskPipeline(
            ollama_client=MockRiskOllamaByTask(),
            ollama_model="test-model",
        ),
    )
    with pytest.raises(ResourceNotFoundError):
        service.generate_risk_recommendations(org_id, run_id)
