from __future__ import annotations

from pathlib import Path

_UUID_SEGMENT = (
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)


def repo_root() -> Path:
    # backend/app/demo_cache/paths.py -> repo root is parents[3]
    return Path(__file__).resolve().parents[3]


def default_cache_dir() -> Path:
    return repo_root() / "demo_cache"


def responses_dir(cache_dir: Path) -> Path:
    return cache_dir / "responses"


def binary_dir(cache_dir: Path) -> Path:
    return cache_dir / "binary"


def ai_dir(cache_dir: Path) -> Path:
    return cache_dir / "ai"


def manifest_path(cache_dir: Path) -> Path:
    return cache_dir / "manifest.json"
