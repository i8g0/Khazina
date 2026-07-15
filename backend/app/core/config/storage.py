from pydantic import Field
from pydantic_settings import BaseSettings

from app.core.config.base import SETTINGS_CONFIG


class StorageSettings(BaseSettings):
    model_config = SETTINGS_CONFIG

    bronze_storage_root: str = Field(default="./data/bronze", min_length=1)
    report_export_storage_root: str = Field(
        default="./data/report_exports", min_length=1
    )
    max_upload_size_bytes: int = Field(default=10_485_760, ge=1)
