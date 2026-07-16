"""Scenario creation integrity — requires at least one assumption."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app.services.exceptions import BusinessValidationError
from app.services.simulation import SimulationService


def test_create_scenario_rejects_empty_assumptions() -> None:
    service = SimulationService(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    service._require_organization = MagicMock()  # type: ignore[method-assign]

    with pytest.raises(BusinessValidationError, match="لا يمكن إنشاء سيناريو"):
        service.create_scenario(
            uuid.uuid4(),
            name="سيناريو تجريبي",
            description="وصف السيناريو",
            assumptions=[],
        )
