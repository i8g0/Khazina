"""Business Engine registry unit tests."""

from __future__ import annotations

import pytest

from app.business.bootstrap import initialize_business_engines
from app.business.engines.risk.manifest import ENGINE_ID as RISK_ENGINE_ID
from app.business.engines.scenario.manifest import ENGINE_ID as SCENARIO_ENGINE_ID
from app.business.engines.waste import WasteEngine
from app.business.engines.waste.manifest import ENGINE_ID
from app.business.exceptions import RegistryFrozenError
from app.business.registry import (
    freeze_registry,
    get_engine,
    get_engine_manifest,
    is_registry_frozen,
    register_engine,
    registered_engine_ids,
    registered_manifests,
)


def test_registry_registration_and_manifest_lookup() -> None:
    register_engine(WasteEngine())
    manifest = get_engine_manifest(ENGINE_ID)

    assert manifest.engine_id == ENGINE_ID
    assert registered_engine_ids() == (ENGINE_ID,)
    assert registered_manifests()[0].engine_name == "Financial Waste Engine"
    assert isinstance(get_engine(ENGINE_ID), WasteEngine)


def test_registry_frozen_after_freeze() -> None:
    register_engine(WasteEngine())
    freeze_registry()

    assert is_registry_frozen()
    with pytest.raises(RegistryFrozenError):
        register_engine(WasteEngine())


def test_bootstrap_registers_and_freezes_engines() -> None:
    initialize_business_engines()

    assert is_registry_frozen()
    assert registered_engine_ids() == (RISK_ENGINE_ID, SCENARIO_ENGINE_ID, ENGINE_ID)
    assert get_engine_manifest(ENGINE_ID).supported_facts
    assert get_engine_manifest(SCENARIO_ENGINE_ID).supported_facts
    assert get_engine_manifest(RISK_ENGINE_ID).supported_facts
