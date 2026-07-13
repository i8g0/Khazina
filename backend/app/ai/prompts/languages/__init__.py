"""Language pack registry — one active language per composed prompt."""

from __future__ import annotations

from app.ai.prompts.languages.ar import ARABIC_PACK
from app.ai.prompts.languages.pack import LanguagePack

_PACKS: dict[str, LanguagePack] = {}


def register_language_pack(pack: LanguagePack) -> None:
    """Register a language pack. Each code may appear once."""
    _PACKS[pack.code] = pack


def get_language_pack(language_code: str) -> LanguagePack:
    """Return the pack for ``language_code`` (single-language content only)."""
    try:
        return _PACKS[language_code]
    except KeyError as exc:
        raise KeyError(f"No language pack registered for: {language_code}") from exc


def supported_languages() -> tuple[str, ...]:
    """Return registered language codes."""
    return tuple(_PACKS.keys())


def _register_builtin_language_packs() -> None:
    register_language_pack(ARABIC_PACK)


_register_builtin_language_packs()
