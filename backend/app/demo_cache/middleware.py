"""ASGI middleware for temporary demo cache replay/recording (hackathon only)."""

from __future__ import annotations

import base64
from typing import Any

from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import get_logger
from app.demo_cache.keys import build_cache_key, build_fallback_keys, should_cache_path
from app.demo_cache.settings import get_demo_cache_settings
from app.demo_cache.store import CacheEntry, DemoCacheStore

logger = get_logger(__name__)


class DemoCacheMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        runtime = get_demo_cache_settings()
        if not runtime.is_active:
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        if request.method == "OPTIONS":
            await self.app(scope, receive, send)
            return

        path = request.url.path
        if not should_cache_path(path):
            await self.app(scope, receive, send)
            return

        store = DemoCacheStore(runtime.cache_dir)
        cache_key = build_cache_key(
            request.method,
            path,
            request.url.query,
        )
        lookup_keys = build_fallback_keys(
            request.method,
            path,
            request.url.query,
        )

        if runtime.enabled:
            entry = store.load_any(lookup_keys)
            if entry is not None:
                hit_key = entry.cache_key
                logger.info("Demo Cache HIT: %s", hit_key)
                response = _entry_to_response(entry)
                await response(scope, receive, send)
                return
            logger.info("Live Execution: %s (cache miss)", cache_key)

        if not runtime.recording:
            await self.app(scope, receive, send)
            return

        body = await request.body()
        messages: list[tuple[Message, bytes | None]] = []

        async def receive_replay() -> Message:
            if body and not messages:
                messages.append(("sent", body))
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        status_holder: dict[str, Any] = {"status": 200, "headers": []}

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                status_holder["status"] = message["status"]
                status_holder["headers"] = list(message.get("headers", []))
            elif message["type"] == "http.response.body":
                chunk = message.get("body", b"")
                status_holder.setdefault("body", b"")
                status_holder["body"] += chunk
                if not message.get("more_body", False):
                    headers = {
                        k.decode("latin-1"): v.decode("latin-1")
                        for k, v in status_holder["headers"]
                    }
                    store.save_from_http(
                        method=request.method,
                        path=path,
                        query=request.url.query,
                        status_code=int(status_holder["status"]),
                        headers=headers,
                        body=status_holder["body"],
                    )
                    logger.info("Demo Cache RECORD: %s", cache_key)
            await send(message)

        await self.app(scope, receive_replay, send_wrapper)


def _entry_to_response(entry: CacheEntry) -> Response:
    headers = dict(entry.headers)
    if entry.body_base64:
        content = base64.b64decode(entry.body_base64)
        return Response(content=content, status_code=entry.status_code, headers=headers)
    return Response(
        content=entry.body_text or "",
        status_code=entry.status_code,
        media_type=headers.get("content-type", "application/json"),
        headers=headers,
    )
