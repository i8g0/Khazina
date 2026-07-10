from app.core.config.app import AppSettings
from app.core.config.database import DatabaseSettings
from app.core.config.logging_config import LoggingSettings


class Settings:
    def __init__(self) -> None:
        self.app = AppSettings()
        self.database = DatabaseSettings()
        self.logging = LoggingSettings()

    @property
    def app_name(self) -> str:
        return self.app.app_name

    @property
    def app_version(self) -> str:
        return self.app.app_version

    @property
    def debug(self) -> bool:
        return self.app.debug

    @property
    def log_level(self) -> str:
        return self.logging.log_level

    @property
    def database_url(self) -> str:
        return self.database.database_url

    @property
    def database_pool_size(self) -> int:
        return self.database.database_pool_size

    @property
    def database_max_overflow(self) -> int:
        return self.database.database_max_overflow

    @property
    def database_pool_pre_ping(self) -> bool:
        return self.database.database_pool_pre_ping


settings = Settings()