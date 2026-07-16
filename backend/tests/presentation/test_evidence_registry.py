"""Evidence registry validation tests."""

from __future__ import annotations

from app.business.engines.waste.engine import WasteEngine
from app.presentation.evidence_registry import EvidenceRegistry
from tests.ai_recommendations.conftest import sample_waste_engine_input


def test_registry_accepts_supported_numbers() -> None:
    contract = WasteEngine().run(sample_waste_engine_input())
    registry = EvidenceRegistry.from_contract(contract)
    text = (
        "خلال الربع الثاني 2026 بلغ الهدر في الشؤون المالية 1,075,000 ريال "
        "الفترة: الربع الثاني 2026\n"
        "قيمة الهدر: 1,075,000 ريال\n"
        "النسبة: 45.9%\n"
        "ويمثل 45.9% من إجمالي الهدر 2,340,000 ريال."
    )
    assert registry.validate_text(text) == []


def test_registry_rejects_forbidden_phrase() -> None:
    contract = WasteEngine().run(sample_waste_engine_input())
    registry = EvidenceRegistry.from_contract(contract)
    text = "تشير البيانات إلى أن الشؤون المالية 1,075,000 ريال بنسبة 45.9%."
    errors = registry.validate_text(text)
    assert any("forbidden_phrase" in err for err in errors)


def test_registry_rejects_unsupported_amount() -> None:
    contract = WasteEngine().run(sample_waste_engine_input())
    registry = EvidenceRegistry.from_contract(contract)
    text = (
        "الشؤون المالية 9,999,999 ريال خلال الربع الثاني 2026 بنسبة 45.9%."
    )
    errors = registry.validate_text(text)
    assert any(err.startswith("unsupported_number") for err in errors)


def test_registry_rejects_arabic_indic_invented_amount() -> None:
    contract = WasteEngine().run(sample_waste_engine_input())
    registry = EvidenceRegistry.from_contract(contract)
    text = "قيمة غير مدعومة ٤٥٠٬٠٠٠ ريال"
    errors = registry.validate_numbers_only(text)
    assert any(err.startswith("unsupported_number") for err in errors)


def test_validate_numbers_only_allows_target_percent() -> None:
    contract = WasteEngine().run(sample_waste_engine_input())
    registry = EvidenceRegistry.from_contract(contract)
    text = "هدف التوفير 10% خلال الفترة."
    assert registry.validate_numbers_only(text) == []


def test_small_riyal_amount_must_match_facts() -> None:
    contract = WasteEngine().run(sample_waste_engine_input())
    registry = EvidenceRegistry.from_contract(contract)
    text = "تكلفة 999 ريال غير مدعومة."
    errors = registry.validate_numbers_only(text)
    assert any(err.startswith("unsupported_number") for err in errors)
