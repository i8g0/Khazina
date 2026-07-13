from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

from app.core.config.base import SETTINGS_CONFIG


class DatabaseSettings(BaseSettings):
    model_config = SETTINGS_CONFIG

    database_url: str = Field(min_length=1)
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_pre_ping: bool = True

    @field_validator("database_url")
    @classmethod
    def database_url_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("DATABASE_URL must not be empty")
        return value
