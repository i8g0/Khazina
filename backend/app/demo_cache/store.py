from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.demo_cache.keys import build_cache_key, cache_key_to_filename
from app.demo_cache.paths import (
    ai_dir,
    binary_dir,
    manifest_path,
    responses_dir,
)


@dataclass
class CacheEntry:
    cache_key: str
    status_code: int
    headers: dict[str, str]
    body_text: str | None = None
    body_base64: str | None = None
    recorded_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CacheEntry:
        return cls(
            cache_key=data["cache_key"],
            status_code=int(data["status_code"]),
            headers=dict(data.get("headers") or {}),
            body_text=data.get("body_text"),
            body_base64=data.get("body_base64"),
            recorded_at=data.get("recorded_at"),
        )


class DemoCacheStore:
    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.responses = responses_dir(cache_dir)
        self.binary = binary_dir(cache_dir)
        self.ai = ai_dir(cache_dir)

    def ensure_layout(self) -> None:
        self.responses.mkdir(parents=True, exist_ok=True)
        self.binary.mkdir(parents=True, exist_ok=True)
        self.ai.mkdir(parents=True, exist_ok=True)

    def response_file(self, cache_key: str) -> Path:
        return self.responses / cache_key_to_filename(cache_key)

    def load(self, cache_key: str) -> CacheEntry | None:
        path = self.response_file(cache_key)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return CacheEntry.from_dict(data)

    def load_any(self, cache_keys: list[str]) -> CacheEntry | None:
        for key in cache_keys:
            entry = self.load(key)
            if entry is not None:
                return entry
        return None

    def save(self, entry: CacheEntry) -> None:
        self.ensure_layout()
        path = self.response_file(entry.cache_key)
        path.write_text(
            json.dumps(entry.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def save_from_http(
        self,
        *,
        method: str,
        path: str,
        query: str,
        status_code: int,
        headers: dict[str, str],
        body: bytes,
    ) -> str:
        cache_key = build_cache_key(method, path, query)
        content_type = headers.get("content-type", "")
        entry: CacheEntry
        if "application/pdf" in content_type or "application/octet-stream" in content_type:
            import base64

            entry = CacheEntry(
                cache_key=cache_key,
                status_code=status_code,
                headers={k: v for k, v in headers.items() if k.lower() != "content-length"},
                body_base64=base64.b64encode(body).decode("ascii"),
                recorded_at=datetime.now(UTC).isoformat(),
            )
        else:
            entry = CacheEntry(
                cache_key=cache_key,
                status_code=status_code,
                headers={k: v for k, v in headers.items() if k.lower() != "content-length"},
                body_text=body.decode("utf-8"),
                recorded_at=datetime.now(UTC).isoformat(),
            )
        self.save(entry)
        return cache_key

    def load_manifest(self) -> dict[str, Any]:
        path = manifest_path(self.cache_dir)
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def save_manifest(self, manifest: dict[str, Any]) -> None:
        self.ensure_layout()
        manifest_path(self.cache_dir).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def ai_response_path(self, key: str) -> Path:
        safe = key.replace("/", "_")
        return self.ai / f"{safe}.json"

    def load_ai_response(self, key: str) -> str | None:
        path = self.ai_response_path(key)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("text")

    def save_ai_response(self, key: str, text: str, *, messages: list[dict[str, str]]) -> None:
        self.ensure_layout()
        payload = {
            "key": key,
            "text": text,
            "messages": messages,
            "recorded_at": datetime.now(UTC).isoformat(),
        }
        self.ai_response_path(key).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def count_responses(self) -> int:
        if not self.responses.exists():
            return 0
        return len(list(self.responses.glob("*.json")))
