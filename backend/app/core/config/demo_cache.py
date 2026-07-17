"""Temporary hackathon demo cache settings — not production architecture."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings

from app.core.config.base import SETTINGS_CONFIG


class DemoCacheSettings(BaseSettings):
    model_config = SETTINGS_CONFIG

    demo_cache_mode: bool = Field(
        default=False,
        description="Serve pre-warmed workflow responses from demo_cache/ (local hackathon only).",
    )
    demo_cache_record: bool = Field(
        default=False,
        description="Record API responses into demo_cache/ during live execution (warming only).",
    )
    demo_cache_dir: str | None = Field(
        default=None,
        description="Absolute path to demo_cache/. Defaults to <repo_root>/demo_cache.",
    )
