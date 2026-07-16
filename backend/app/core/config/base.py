from pathlib import Path

from pydantic_settings import SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[3]

SETTINGS_CONFIG = SettingsConfigDict(
    env_file=_BACKEND_DIR / ".env",
    env_file_encoding="utf-8",
    case_sensitive=False,
    extra="ignore",
)