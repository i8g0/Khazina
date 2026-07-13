"""Prompt-layer fact input for prompt construction (Sprint 5.2).

``PromptFact`` is a prompt-layer type only. It is not the Facts Contract —
Business Engines will produce the official Facts Contract in a future sprint;
upstream layers map contract facts to ``PromptFact`` before calling the
Prompt Engine.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PromptFact:
    """A single fact prepared for inclusion in a user prompt."""

    domain: str
    metric: str
    value: str
    unit: str | None = None
    severity: str | None = None
    confidence: str | None = None
    source: str | None = None
