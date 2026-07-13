from app.core.config.app import AppSettings
from app.core.config.ai import AiSettings
from app.core.config.auth import AuthSettings
from app.core.config.database import DatabaseSettings
from app.core.config.logging_config import LoggingSettings


class Settings:
    def __init__(self) -> None:
        self.app = AppSettings()
        self.ai = AiSettings()
        self.auth = AuthSettings()
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

    @property
    def jwt_secret_key(self) -> str:
        return self.auth.jwt_secret_key

    @property
    def jwt_algorithm(self) -> str:
        return self.auth.jwt_algorithm

    @property
    def jwt_access_token_expire_minutes(self) -> int:
        return self.auth.jwt_access_token_expire_minutes

    @property
    def ollama_url(self) -> str:
        return str(self.ai.ollama_url)

    @property
    def ollama_model(self) -> str:
        return self.ai.ollama_model

    @property
    def ai_timeout(self) -> float:
        return self.ai.ai_timeout


settings = Settings()