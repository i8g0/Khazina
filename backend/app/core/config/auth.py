from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

from app.core.config.base import SETTINGS_CONFIG


class AuthSettings(BaseSettings):
    model_config = SETTINGS_CONFIG

    jwt_secret_key: str = Field(min_length=1)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    @field_validator("jwt_secret_key")
    @classmethod
    def jwt_secret_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("JWT_SECRET_KEY must not be empty")
        return value
