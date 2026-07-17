from __future__ import annotations

from typing import Literal

from pydantic import Field, HttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings

from app.core.config.base import SETTINGS_CONFIG


class AiSettings(BaseSettings):
    model_config = SETTINGS_CONFIG

    ai_provider: Literal["ollama", "cloud"] = Field(
        default="ollama",
        description="Active inference backend (AI_PROVIDER): ollama | cloud",
    )

    ollama_url: HttpUrl | None = Field(
        default=None,
        description="Base URL for the Ollama HTTP API (OLLAMA_URL)",
    )
    ollama_model: str | None = Field(
        default=None,
        description="Ollama model identifier (OLLAMA_MODEL)",
    )

    cloud_ai_base_url: HttpUrl | None = Field(
        default=None,
        description=(
            "OpenAI-compatible API base URL (CLOUD_AI_BASE_URL), "
            "e.g. https://api.openai.com/v1"
        ),
    )
    cloud_ai_model: str | None = Field(
        default=None,
        description="Cloud model identifier (CLOUD_AI_MODEL)",
    )
    cloud_ai_api_key: str | None = Field(
        default=None,
        description="Cloud provider API key (CLOUD_AI_API_KEY) — never logged",
    )

    ai_timeout: float = Field(
        default=30.0,
        gt=0,
        le=300,
        description="HTTP timeout in seconds for AI provider requests (AI_TIMEOUT)",
    )
    ai_temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
        description=(
            "Sampling temperature for cloud completions (AI_TEMPERATURE) — "
            "interpretation layer must be near-deterministic"
        ),
    )
    guard_max_retries: int = Field(
        default=1,
        ge=0,
        le=3,
        description="Corrective retries when number guard rejects narrative (GUARD_MAX_RETRIES)",
    )
    default_prompt_language: str = Field(
        default="ar",
        min_length=2,
        max_length=16,
        description=(
            "Default prompt language code for Prompt Engine output (DEFAULT_PROMPT_LANGUAGE)"
        ),
    )
    ai_parallel_tasks: bool | None = Field(
        default=None,
        description=(
            "Run independent AI tasks concurrently (AI_PARALLEL_TASKS). "
            "Defaults to true when AI_PROVIDER=cloud."
        ),
    )

    @field_validator("default_prompt_language")
    @classmethod
    def default_prompt_language_normalized(cls, value: str) -> str:
        language = value.strip().lower()
        if not language:
            raise ValueError("DEFAULT_PROMPT_LANGUAGE must not be empty")
        return language

    @field_validator("ollama_model", "cloud_ai_model")
    @classmethod
    def strip_optional_model(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @property
    def active_model(self) -> str:
        if self.ai_provider == "cloud":
            return self.cloud_ai_model or ""
        return self.ollama_model or ""

    @property
    def parallel_tasks_enabled(self) -> bool:
        if self.ai_parallel_tasks is not None:
            return self.ai_parallel_tasks
        return self.ai_provider == "cloud"

    def validate_provider_config(self) -> None:
        """Ensure provider-specific required settings are present."""
        if self.ai_provider == "ollama":
            if self.ollama_url is None:
                raise ValueError("OLLAMA_URL is required when AI_PROVIDER=ollama")
            if not (self.ollama_model or "").strip():
                raise ValueError("OLLAMA_MODEL is required when AI_PROVIDER=ollama")
            return
        if self.ai_provider == "cloud":
            if self.cloud_ai_base_url is None:
                raise ValueError(
                    "CLOUD_AI_BASE_URL is required when AI_PROVIDER=cloud"
                )
            if not (self.cloud_ai_model or "").strip():
                raise ValueError("CLOUD_AI_MODEL is required when AI_PROVIDER=cloud")
            if not (self.cloud_ai_api_key or "").strip():
                raise ValueError("CLOUD_AI_API_KEY is required when AI_PROVIDER=cloud")
            return
        raise ValueError(f"Unsupported AI_PROVIDER: {self.ai_provider}")

    @model_validator(mode="after")
    def validate_on_load(self) -> AiSettings:
        self.validate_provider_config()
        return self
