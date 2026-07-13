from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings

from app.core.config.base import SETTINGS_CONFIG


class AiSettings(BaseSettings):
    model_config = SETTINGS_CONFIG

    ollama_url: HttpUrl = Field(
        description="Base URL for the Ollama HTTP API (OLLAMA_URL)",
    )
    ollama_model: str = Field(
        min_length=1,
        description=(
            "Ollama model identifier supplied by the deployment environment "
            "(OLLAMA_MODEL); not hardcoded in application code"
        ),
    )
    ai_timeout: float = Field(
        default=30.0,
        gt=0,
        le=300,
        description="HTTP timeout in seconds for Ollama requests (AI_TIMEOUT)",
    )

    @field_validator("ollama_model")
    @classmethod
    def ollama_model_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("OLLAMA_MODEL must not be empty")
        return value.strip()
