from pydantic_settings import BaseSettings

from app.core.config.base import SETTINGS_CONFIG


class AppSettings(BaseSettings):
    model_config = SETTINGS_CONFIG

    app_name: str = "Khazina API"
    app_version: str = "0.1.0"
    debug: bool = False