"""AiRecommendationService orchestration tests."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app.ai.prompts.tasks import PromptTask
from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.pipeline import AiTaskPipeline
from app.ai_recommendations.service import AiRecommendationService
from app.db.models.enums import AnalysisRunStatus, AnalysisType, RecommendationDomain
from app.services.exceptions import InvalidStateError, ResourceNotFoundError
from tests.ai_recommendations.conftest import (
    MockOllamaByTask,
    sample_facts_contract,
)


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def run_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def snapshot_id() -> uuid.UUID:
    return uuid.uuid4()


def _completed_run(
    org_id: uuid.UUID, run_id: uuid.UUID, snapshot_id: uuid.UUID
) -> MagicMock:
    facts = sample_facts_contract()
    run = MagicMock()
    run.id = run_id
    run.organization_id = org_id
    run.source_snapshot_id = snapshot_id
    run.analysis_type = AnalysisType.FINANCIAL_WASTE
    run.status = AnalysisRunStatus.COMPLETED
    run.runtime_metadata = {"facts_contract": facts.to_dict()}
    return run


def _service(
    run: MagicMock,
    *,
    mock_ollama: MockOllamaByTask | None = None,
    waste_result: MagicMock | None = None,
) -> AiRecommendationService:
    session = MagicMock()
    analysis_repo = MagicMock()
    waste_repo = MagicMock()
    recommendation_repo = MagicMock()

    analysis_repo.get.return_value = run
    analysis_repo.update.side_effect = lambda r, values: setattr(
        r, "runtime_metadata", values["runtime_metadata"]
    ) or r
    waste_repo.get_result_for_run.return_value = waste_result or MagicMock()
    recommendation_repo.list_for_analysis_run.return_value = []
    recommendation_repo.create.side_effect = lambda rec: rec

    pipeline = AiTaskPipeline(
        ollama_client=mock_ollama or MockOllamaByTask(),
        ollama_model="test-model",
        prompt_language="ar",
    )
    return AiRecommendationService(
        session,
        analysis_repo,
        waste_repo,
        recommendation_repo,
        task_pipeline=pipeline,
    )


def test_generate_success(
    org_id: uuid.UUID, run_id: uuid.UUID, snapshot_id: uuid.UUID
) -> None:
    run = _completed_run(org_id, run_id, snapshot_id)
    service = _service(run)
    outcome = service.generate_waste_recommendations(org_id, run_id)

    assert outcome.ai_insights["executive_summary"]
    assert outcome.ai_insights["risk_explanation"]
    assert outcome.ai_insights["prompt_version"] == "1.0"
    assert outcome.ai_insights["source_snapshot_id"] == str(snapshot_id)
    assert len(outcome.recommendations) == 3
    assert run.runtime_metadata["ai_insights"]


def test_rejects_non_completed_run(
    org_id: uuid.UUID, run_id: uuid.UUID, snapshot_id: uuid.UUID
) -> None:
    run = _completed_run(org_id, run_id, snapshot_id)
    run.status = AnalysisRunStatus.PROCESSING
    service = _service(run)
    with pytest.raises(InvalidStateError):
        service.generate_waste_recommendations(org_id, run_id)


def test_rejects_missing_gold_result(
    org_id: uuid.UUID, run_id: uuid.UUID, snapshot_id: uuid.UUID
) -> None:
    run = _completed_run(org_id, run_id, snapshot_id)
    service = _service(run, waste_result=None)
    waste_repo = service._waste
    waste_repo.get_result_for_run.return_value = None
    with pytest.raises(InvalidStateError):
        service.generate_waste_recommendations(org_id, run_id)


def test_idempotency_guard(
    org_id: uuid.UUID, run_id: uuid.UUID, snapshot_id: uuid.UUID
) -> None:
    run = _completed_run(org_id, run_id, snapshot_id)
    run.runtime_metadata["ai_insights"] = {"generated_at": "2026-01-01"}
    service = _service(run)
    with pytest.raises(AiRecommendationError) as exc:
        service.generate_waste_recommendations(org_id, run_id)
    assert exc.value.error_code == "ai_insights_already_exist"


def test_regenerate_deletes_waste_recommendations(
    org_id: uuid.UUID, run_id: uuid.UUID, snapshot_id: uuid.UUID
) -> None:
    run = _completed_run(org_id, run_id, snapshot_id)
    run.runtime_metadata["ai_insights"] = {"generated_at": "2026-01-01"}
    existing = MagicMock()
    existing.domain_source = RecommendationDomain.WASTE
    service = _service(run)
    service._recommendation_repo.list_for_analysis_run.return_value = [existing]

    service.generate_waste_recommendations(org_id, run_id, regenerate=True)
    service._recommendation_repo.delete.assert_called_once_with(existing)


def test_missing_run_raises_not_found(org_id: uuid.UUID, run_id: uuid.UUID) -> None:
    session = MagicMock()
    analysis_repo = MagicMock()
    analysis_repo.get.return_value = None
    service = AiRecommendationService(
        session,
        analysis_repo,
        MagicMock(),
        MagicMock(),
        task_pipeline=AiTaskPipeline(
            ollama_client=MockOllamaByTask(),
            ollama_model="test-model",
        ),
    )
    with pytest.raises(ResourceNotFoundError):
        service.generate_waste_recommendations(org_id, run_id)


def test_pipeline_executes_three_tasks_in_order(
    org_id: uuid.UUID, run_id: uuid.UUID, snapshot_id: uuid.UUID
) -> None:
    mock = MockOllamaByTask()
    run = _completed_run(org_id, run_id, snapshot_id)
    service = _service(run, mock_ollama=mock)
    service.generate_waste_recommendations(org_id, run_id)
    assert mock.calls == [
        PromptTask.EXECUTIVE_SUMMARY,
        PromptTask.RECOMMENDATIONS,
        PromptTask.RISK_ANALYSIS,
    ]
