from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

from app.ai.providers.base import AIProvider
from app.core.logging import get_logger
from app.demo_cache.settings import get_demo_cache_settings
from app.demo_cache.store import DemoCacheStore

logger = get_logger(__name__)


def _ai_cache_key(messages: list[dict[str, str]], *, model: str | None) -> str:
    payload = json.dumps(
        {"model": model, "messages": messages},
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


class DemoCacheAIProvider(AIProvider):
    """Wraps a real provider; replays or records genuine LLM outputs only."""

    def __init__(self, inner: AIProvider, store: DemoCacheStore) -> None:
        self._inner = inner
        self._store = store
        self._runtime = get_demo_cache_settings()

    @property
    def provider_name(self) -> str:
        return self._inner.provider_name

    @property
    def configured_model(self) -> str:
        return self._inner.configured_model

    @property
    def timeout_seconds(self) -> float:
        return self._inner.timeout_seconds

    def check_connectivity(self) -> None:
        if self._runtime.enabled and self._store.count_responses() > 0:
            return
        self._inner.check_connectivity()

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        format_json: bool = False,
        think: bool = False,
    ) -> str:
        key = _ai_cache_key(messages, model=model)
        if self._runtime.enabled:
            cached = self._store.load_ai_response(key)
            if cached is not None:
                logger.info("Demo Cache HIT: AI chat key=%s", key)
                return cached
            logger.info("Live Execution: AI chat key=%s (cache miss)", key)

        text = self._inner.chat(
            messages,
            model=model,
            format_json=format_json,
            think=think,
        )
        if self._runtime.recording:
            self._store.save_ai_response(key, text, messages=messages)
            logger.info("Demo Cache RECORD: AI chat key=%s", key)
        return text

    def close(self) -> None:
        self._inner.close()
