from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "Khazina API"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    database_url: str = "postgresql://khazina:khazina@localhost:5432/khazina"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_pre_ping: bool = True


settings = Settings()