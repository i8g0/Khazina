from pydantic_settings import BaseSettings

from app.core.config.base import SETTINGS_CONFIG


class DatabaseSettings(BaseSettings):
    model_config = SETTINGS_CONFIG

    database_url: str = "postgresql://khazina:khazina@localhost:5432/khazina"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_pre_ping: bool = True