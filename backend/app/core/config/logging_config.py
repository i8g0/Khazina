from pydantic_settings import BaseSettings

from app.core.config.base import SETTINGS_CONFIG


class LoggingSettings(BaseSettings):
    model_config = SETTINGS_CONFIG

    log_level: str = "INFO"