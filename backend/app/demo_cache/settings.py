from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.config.demo_cache import DemoCacheSettings
from app.demo_cache.paths import default_cache_dir


@dataclass(frozen=True)
class DemoCacheRuntime:
    enabled: bool
    recording: bool
    cache_dir: Path

    @property
    def is_active(self) -> bool:
        return self.enabled or self.recording


def get_demo_cache_settings() -> DemoCacheRuntime:
    cfg = DemoCacheSettings()
    cache_dir = Path(cfg.demo_cache_dir) if cfg.demo_cache_dir else default_cache_dir()
    return DemoCacheRuntime(
        enabled=cfg.demo_cache_mode,
        recording=cfg.demo_cache_record,
        cache_dir=cache_dir,
    )
