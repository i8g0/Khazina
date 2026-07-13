from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

from app.core.config.base import SETTINGS_CONFIG

_ALLOWED_JWT_ALGORITHMS = frozenset({"HS256"})


class AuthSettings(BaseSettings):
    model_config = SETTINGS_CONFIG

    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=60, ge=1, le=24 * 60)

    @field_validator("jwt_secret_key")
    @classmethod
    def jwt_secret_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("JWT_SECRET_KEY must not be empty")
        return value

    @field_validator("jwt_algorithm")
    @classmethod
    def jwt_algorithm_allowed(cls, value: str) -> str:
        algorithm = value.strip().upper()
        if algorithm not in _ALLOWED_JWT_ALGORITHMS:
            allowed = ", ".join(sorted(_ALLOWED_JWT_ALGORITHMS))
            raise ValueError(
                f"JWT_ALGORITHM must be one of: {allowed}"
            )
        return algorithm
