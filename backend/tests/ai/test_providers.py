"""AI provider abstraction tests (Phase 10)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.ai.exceptions import AIConfigurationError, AIConnectionError, AITimeoutError
from app.ai.health import check_ai_provider_health
from app.ai.telemetry import clear_ai_request_records, get_ai_request_records
from app.ai.providers.cloud import CloudProvider
from app.ai.providers.factory import create_ai_provider
from app.ai.providers.ollama import OllamaProvider
from app.core.config.ai import AiSettings


def _ollama_settings(**overrides: object) -> AiSettings:
    base = {
        "ai_provider": "ollama",
        "ollama_url": "http://localhost:11434",
        "ollama_model": "qwen3:8b",
        "ai_timeout": 5.0,
    }
    base.update(overrides)
    return AiSettings.model_construct(**base)  # type: ignore[arg-type]


def _cloud_settings(**overrides: object) -> AiSettings:
    base = {
        "ai_provider": "cloud",
        "cloud_ai_base_url": "https://api.example.com/v1",
        "cloud_ai_model": "gpt-4o-mini",
        "cloud_ai_api_key": "test-key",
        "ai_timeout": 5.0,
        "ai_temperature": 0.2,
    }
    base.update(overrides)
    return AiSettings.model_construct(**base)  # type: ignore[arg-type]


def test_factory_selects_ollama_by_default() -> None:
    provider = create_ai_provider(_ollama_settings())
    assert isinstance(provider, OllamaProvider)
    assert provider.provider_name == "ollama"
    assert provider.configured_model == "qwen3:8b"


def test_factory_selects_cloud_when_configured() -> None:
    provider = create_ai_provider(_cloud_settings())
    assert isinstance(provider, CloudProvider)
    assert provider.provider_name == "cloud"
    assert provider.configured_model == "gpt-4o-mini"


def test_factory_rejects_unknown_provider() -> None:
    settings = _ollama_settings(ai_provider="unknown")
    with pytest.raises(AIConfigurationError):
        create_ai_provider(settings)


def test_ollama_chat_returns_assistant_content() -> None:
    provider = OllamaProvider(_ollama_settings())
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "message": {"role": "assistant", "content": "hello from ollama"}
    }
    mock_client = MagicMock()
    mock_client.post.return_value = mock_response

    with patch.object(provider, "_client", return_value=mock_client):
        text = provider.chat([{"role": "user", "content": "hi"}])

    assert text == "hello from ollama"
    payload = mock_client.post.call_args.kwargs["json"]
    assert payload["model"] == "qwen3:8b"
    assert payload["stream"] is False


def test_cloud_chat_returns_assistant_content() -> None:
    provider = CloudProvider(_cloud_settings())
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": "hello from cloud"}}]
    }
    mock_client = MagicMock()
    mock_client.post.return_value = mock_response

    with patch.object(provider, "_client", return_value=mock_client):
        text = provider.chat([{"role": "user", "content": "hi"}], format_json=True)

    assert text == "hello from cloud"
    headers = mock_client.post.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer test-key"
    payload = mock_client.post.call_args.kwargs["json"]
    assert payload["response_format"] == {"type": "json_object"}


def test_ollama_connectivity_timeout_normalized() -> None:
    provider = OllamaProvider(_ollama_settings())
    mock_client = MagicMock()
    mock_client.get.side_effect = httpx.TimeoutException("timeout")

    with patch.object(provider, "_client", return_value=mock_client):
        with pytest.raises(AITimeoutError):
            provider.check_connectivity()


def test_cloud_connectivity_failure_normalized() -> None:
    provider = CloudProvider(_cloud_settings())
    mock_client = MagicMock()
    mock_client.get.side_effect = httpx.ConnectError("down")

    with patch.object(provider, "_client", return_value=mock_client):
        with pytest.raises(AIConnectionError):
            provider.check_connectivity()


def test_health_reports_provider_without_secrets() -> None:
    provider = CloudProvider(_cloud_settings())
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    with patch.object(provider, "_client", return_value=mock_client):
        result = check_ai_provider_health(provider)

    assert result.status == "ok"
    assert result.provider == "cloud"
    assert result.provider_reachable is True
    assert result.ollama_reachable is True
    assert result.configured_model == "gpt-4o-mini"
    assert "test-key" not in result.message


def test_health_sets_legacy_ollama_reachable_when_provider_ok() -> None:
    provider = CloudProvider(_cloud_settings())
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    with patch.object(provider, "_client", return_value=mock_client):
        result = check_ai_provider_health(provider)

    assert result.provider == "cloud"
    assert result.provider_reachable is True
    assert result.ollama_reachable is True


def test_cloud_chat_records_telemetry() -> None:
    provider = CloudProvider(_cloud_settings())
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": "hello"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }
    mock_client = MagicMock()
    mock_client.post.return_value = mock_response

    clear_ai_request_records()
    with patch.object(provider, "_client", return_value=mock_client):
        provider.chat([{"role": "user", "content": "hi"}])

    records = get_ai_request_records()
    assert len(records) == 1
    assert records[0].provider == "cloud"
    assert records[0].model == "gpt-4o-mini"
    assert records[0].endpoint.endswith("/chat/completions")
    clear_ai_request_records()


def test_ai_settings_active_model_follows_provider() -> None:
    assert _ollama_settings().active_model == "qwen3:8b"
    assert _cloud_settings().active_model == "gpt-4o-mini"
