"""Shared fixtures for Business Engine tests."""

from __future__ import annotations

import pytest

from app.business.registry import reset_registry_for_testing


@pytest.fixture(autouse=True)
def reset_registry() -> None:
    reset_registry_for_testing()
