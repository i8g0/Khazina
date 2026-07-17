from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode

_UUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)

_SKIP_PREFIXES = (
    "/api/v1/health",
    "/api/v1/ai/health",
    "/docs",
    "/openapi.json",
    "/redoc",
)

# Auth must stay live — cached JWTs expire and break the whole workflow.
_SKIP_EXACT_SUFFIXES = (
    "/auth/login",
    "/organizations/active",
)


def should_cache_path(path: str) -> bool:
    if not path.startswith("/api/v1/"):
        return False
    if any(path.startswith(prefix) for prefix in _SKIP_PREFIXES):
        return False
    normalized = normalize_api_path(path)
    if any(normalized.endswith(suffix) for suffix in _SKIP_EXACT_SUFFIXES):
        return False
    return True


def normalize_path(path: str) -> str:
    normalized = _UUID_RE.sub("{id}", path)
    return normalized.rstrip("/") or "/"


def normalize_query(query: str) -> str:
    if not query:
        return ""
    pairs = parse_qsl(query, keep_blank_values=True)
    pairs.sort(key=lambda item: item[0])
    return urlencode(pairs)


def normalize_api_path(path: str) -> str:
    """Strip /api/v1 prefix so cache keys match warmer and middleware."""
    if path.startswith("/api/v1"):
        path = path[len("/api/v1") :] or "/"
    return normalize_path(path)


def build_cache_key(method: str, path: str, query: str = "") -> str:
    norm_path = normalize_api_path(path)
    norm_query = normalize_query(query)
    if norm_query:
        return f"{method.upper()} {norm_path}?{norm_query}"
    return f"{method.upper()} {norm_path}"


_POST_FALLBACK_SUFFIXES = (
    "/financial-files/upload",
    "/decisions/waste/execute",
    "/ai-recommendations/waste/generate",
    "/ai-recommendations/risk/generate",
    "/risk-analyses/execute",
    "/simulation/ai/execute",
    "/reports/generate",
)


def build_fallback_keys(method: str, path: str, query: str = "") -> list[str]:
    """Alternative keys when exact query/body differs (POST execute endpoints)."""
    keys = [build_cache_key(method, path, query)]
    norm = normalize_api_path(path)
    if method.upper() == "POST":
        for suffix in _POST_FALLBACK_SUFFIXES:
            if norm.endswith(suffix) or norm.endswith(suffix.rstrip("/")):
                keys.append(build_cache_key(method, path, ""))
                break
    return keys


def cache_key_to_filename(cache_key: str) -> str:
    safe = cache_key.replace("/", "_").replace("?", "__").replace("&", "_").replace("=", "-")
    safe = re.sub(r"[^\w.\-{}]", "_", safe)
    return f"{safe}.json"
