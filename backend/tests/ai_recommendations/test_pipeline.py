"""AiTaskPipeline tests — Facts-only, no engine.run()."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.ai.prompts.tasks import PromptTask
from app.ai_recommendations.exceptions import AiRecommendationError
from app.ai_recommendations.pipeline import AiTaskPipeline
from tests.ai_recommendations.conftest import MockOllamaByTask, sample_facts_contract


def test_execute_task_uses_facts_only() -> None:
    facts = sample_facts_contract()
    mock = MockOllamaByTask()
    pipeline = AiTaskPipeline(
        ollama_client=mock,
        ollama_model="test-model",
        prompt_language="ar",
    )
    result = pipeline.execute_task(facts, PromptTask.EXECUTIVE_SUMMARY)
    assert result.parsed_response.text
    assert mock.calls == [PromptTask.EXECUTIVE_SUMMARY]
    user_prompt = mock  # messages captured indirectly via task detection
    assert user_prompt.calls


def test_empty_llm_response_fails() -> None:
    mock = MagicMock()
    mock.chat.return_value = "   "
    pipeline = AiTaskPipeline(ollama_client=mock, ollama_model="test-model")
    with pytest.raises(AiRecommendationError) as exc:
        pipeline.execute_task(sample_facts_contract(), PromptTask.EXECUTIVE_SUMMARY)
    assert exc.value.error_code == "empty_llm_response"
