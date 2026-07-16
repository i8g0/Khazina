"""Evidence registry for validating AI recommendations against Facts Contract."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from app.business.facts.contract import FactsContract
from app.presentation.business_labels import (
    category_label_ar,
    contains_english_category_leakage,
)
from app.presentation.waste_category_labels import waste_category_label_ar

_FORBIDDEN_PHRASES: tuple[str, ...] = (
    "تشير البيانات",
    "قد يكون",
    "ربما",
    "يمكن",
    "من الممكن",
    "قد يساعد",
    "there are",
    "the data suggests",
    "high category",
    "low category",
    "medium category",
    "الفئة المالية مرتفعة",
    "فئة مرتفعة",
    "فئة منخفضة",
    "فئة متوسطة",
    "هناك فئة",
    "بعض الفئات",
    "الفئات عالية",
    "الفئات منخفضة",
    "يُوصى بشكل عام",
    "توصية عامة",
    "يُنصح بشكل عام",
)

_GENERIC_CATEGORY_PHRASES: tuple[str, ...] = (
    "هناك فئة",
    "الفئة ",
    "بعض الفئات",
    "الفئات عالية",
    "الفئات منخفضة",
    "فئة مرتفعة",
    "فئة منخفضة",
)

_NUMBER_TOKEN = re.compile(
    r"(?<!\w)(?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?!\w)"
)


@dataclass
class EvidenceRegistry:
    """Collects verifiable tokens from a Facts Contract for parser validation."""

    period: str | None = None
    organization_id: str | None = None
    category_codes: set[str] = field(default_factory=set)
    category_labels_ar: set[str] = field(default_factory=set)
    amounts: set[Decimal] = field(default_factory=set)
    percentages: set[Decimal] = field(default_factory=set)
    currency_values: set[str] = field(default_factory=set)

    @classmethod
    def from_contract(cls, contract: FactsContract) -> EvidenceRegistry:
        registry = cls()
        for fact in contract.facts:
            if fact.period and not registry.period:
                registry.period = fact.period
            if fact.organization_id and not registry.organization_id:
                registry.organization_id = fact.organization_id

            category_name = (fact.metadata or {}).get("category_name")
            if category_name:
                code = str(category_name).strip().lower()
                registry.category_codes.add(code)
                label = (fact.metadata or {}).get("category_label_ar") or waste_category_label_ar(code)
                registry.category_labels_ar.add(label)

            if fact.unit == "currency":
                registry._register_amount(fact.value)
            elif fact.unit == "percent":
                registry._register_percentage(fact.value)
            elif fact.metric == "waste.top_category" and fact.value:
                code = fact.value.strip().lower()
                registry.category_codes.add(code)
                registry.category_labels_ar.add(waste_category_label_ar(code))

        period_ext = (contract.extensions or {}).get("executive_context", {}).get(
            "reporting_period_label"
        )
        if period_ext:
            registry.period = str(period_ext)

        return registry

    def _register_amount(self, raw: str) -> None:
        try:
            value = Decimal(str(raw).replace(",", ""))
        except InvalidOperation:
            return
        registry_amount = value
        self.amounts.add(registry_amount)
        self.currency_values.add(f"{value:.2f}")
        if value >= 1_000_000:
            self.currency_values.add(f"{value / Decimal('1000000'):.2f}")
        if value >= 1_000:
            self.currency_values.add(f"{value / Decimal('1000'):.0f}")

    def _register_percentage(self, raw: str) -> None:
        try:
            self.percentages.add(Decimal(str(raw).replace(",", "")))
        except InvalidOperation:
            return

    def validate_text(self, text: str) -> list[str]:
        """Return validation errors; empty list means acceptable."""
        errors: list[str] = []
        lowered = text.lower()

        for phrase in _FORBIDDEN_PHRASES:
            if phrase.lower() in lowered or phrase in text:
                errors.append(f"forbidden_phrase:{phrase}")

        if not self._has_category_reference(text):
            errors.append("missing_category_reference")

        if self._has_generic_category_wording(text):
            errors.append("generic_category_wording")

        if contains_english_category_leakage(text):
            errors.append("english_category_leakage")

        if not self._has_structured_evidence(text):
            errors.append("missing_structured_evidence")

        if not self._has_numeric_evidence(text):
            errors.append("missing_numeric_evidence")

        for number, is_percent in _extract_significant_numbers(text):
            if not self._number_is_supported(number, is_percent=is_percent):
                errors.append(f"unsupported_number:{number}")

        if len(text.strip()) < 80:
            errors.append("recommendation_too_short")

        return errors

    def _has_category_reference(self, text: str) -> bool:
        if self.category_labels_ar:
            return any(label in text for label in self.category_labels_ar if label)
        if self.category_codes:
            return any(
                category_label_ar(code) in text for code in self.category_codes
            )
        return True

    def _has_generic_category_wording(self, text: str) -> bool:
        for phrase in _GENERIC_CATEGORY_PHRASES:
            if phrase in text and not any(label in text for label in self.category_labels_ar):
                return True
        return False

    def _has_structured_evidence(self, text: str) -> bool:
        tokens = ("الفترة:", "قيمة الهدر:", "النسبة:")
        return sum(1 for token in tokens if token in text) >= 2

    def _has_numeric_evidence(self, text: str) -> bool:
        return bool(_extract_significant_numbers(text))

    def _number_is_supported(self, number: Decimal, *, is_percent: bool) -> bool:
        if Decimal("1900") <= number <= Decimal("2100"):
            return True
        if is_percent:
            for pct in self.percentages:
                if _numbers_close(number, pct):
                    return True
            # KPI target percentages (e.g. 8%, 10%) are allowed — not waste facts.
            if number <= Decimal("20"):
                return True
            return False
        if number < Decimal("1000"):
            return True
        for amount in self.amounts:
            if _numbers_close(number, amount):
                return True
            if amount >= 1_000_000 and _numbers_close(number, amount / Decimal("1000000")):
                return True
            if amount >= 1_000 and _numbers_close(number, amount / Decimal("1000")):
                return True
        for pct in self.percentages:
            if _numbers_close(number, pct):
                return True
        return False


def _extract_significant_numbers(text: str) -> list[tuple[Decimal, bool]]:
    values: list[tuple[Decimal, bool]] = []
    for match in _NUMBER_TOKEN.finditer(text):
        token = match.group(0).replace(",", "")
        try:
            number = Decimal(token)
        except InvalidOperation:
            continue
        tail = text[match.end() : match.end() + 3]
        is_percent = "%" in tail or "٪" in tail
        if number >= Decimal("1000") or is_percent:
            if Decimal("1900") <= number <= Decimal("2100") and not is_percent:
                continue
            values.append((number, is_percent))
    return values


def _numbers_close(a: Decimal, b: Decimal, *, tolerance: Decimal = Decimal("0.05")) -> bool:
    if b == 0:
        return a == 0
    return abs(a - b) / abs(b) <= tolerance or abs(a - b) <= Decimal("1")