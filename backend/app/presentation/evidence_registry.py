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

_ARABIC_INDIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
_ALLOWED_TARGET_PERCENTS: frozenset[Decimal] = frozenset(
    Decimal(str(v)) for v in (5, 8, 10, 15, 20)
)


def normalize_text(text: str) -> str:
    """Normalize Arabic numerals and punctuation before number extraction."""
    normalized = text.translate(_ARABIC_INDIC_DIGITS).translate(_PERSIAN_DIGITS)
    normalized = normalized.replace("٬", ",").replace("،", ",")
    normalized = normalized.replace("٫", ".").replace("٪", "%")
    return normalized


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
        return self._validate_core(text, require_structure=True)

    def validate_numbers_only(self, text: str) -> list[str]:
        """Lean guard: forbidden phrases + unsupported numbers only."""
        return self._validate_core(text, require_structure=False)

    def validate_risk_text(self, text: str) -> list[str]:
        """Risk recommendations: numbers + forbidden phrases, no waste structure."""
        return self._validate_core(text, require_structure=False)

    def _validate_core(self, text: str, *, require_structure: bool) -> list[str]:
        normalized = normalize_text(text)
        errors: list[str] = []
        lowered = normalized.lower()

        for phrase in _FORBIDDEN_PHRASES:
            if phrase.lower() in lowered or phrase in normalized:
                errors.append(f"forbidden_phrase:{phrase}")

        if require_structure:
            if not self._has_category_reference(normalized):
                errors.append("missing_category_reference")

            if self._has_generic_category_wording(normalized):
                errors.append("generic_category_wording")

            if contains_english_category_leakage(normalized):
                errors.append("english_category_leakage")

            if not self._has_structured_evidence(normalized):
                errors.append("missing_structured_evidence")

            if not self._has_numeric_evidence(normalized):
                errors.append("missing_numeric_evidence")

        for number, is_percent, followed_by_riyal in _extract_significant_numbers(
            normalized
        ):
            if not self._number_is_supported(
                number, is_percent=is_percent, followed_by_riyal=followed_by_riyal
            ):
                errors.append(f"unsupported_number:{number}")

        if require_structure and len(normalized.strip()) < 80:
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

    def _number_is_supported(
        self,
        number: Decimal,
        *,
        is_percent: bool,
        followed_by_riyal: bool = False,
    ) -> bool:
        if Decimal("1900") <= number <= Decimal("2100"):
            return True
        if is_percent:
            for pct in self.percentages:
                if _numbers_close(number, pct):
                    return True
            if number in _ALLOWED_TARGET_PERCENTS:
                return True
            return False
        if number < Decimal("1000"):
            if followed_by_riyal:
                return self._amount_matches_facts(number)
            return True
        return self._amount_matches_facts(number)

    def _amount_matches_facts(self, number: Decimal) -> bool:
        for amount in self.amounts:
            if _numbers_close(number, amount):
                return True
            if amount >= 1_000_000 and _numbers_close(
                number, amount / Decimal("1000000")
            ):
                return True
            if amount >= 1_000 and _numbers_close(number, amount / Decimal("1000")):
                return True
        for pct in self.percentages:
            if _numbers_close(number, pct):
                return True
        return False


def _extract_significant_numbers(
    text: str,
) -> list[tuple[Decimal, bool, bool]]:
    normalized = normalize_text(text)
    values: list[tuple[Decimal, bool, bool]] = []
    for match in _NUMBER_TOKEN.finditer(normalized):
        token = match.group(0).replace(",", "")
        try:
            number = Decimal(token)
        except InvalidOperation:
            continue
        tail = normalized[match.end() : match.end() + 12]
        is_percent = "%" in tail[:3]
        followed_by_riyal = tail.lstrip().startswith("ريال")
        if number >= Decimal("1000") or is_percent or followed_by_riyal:
            if Decimal("1900") <= number <= Decimal("2100") and not is_percent:
                continue
            values.append((number, is_percent, followed_by_riyal))
    return values


def _numbers_close(a: Decimal, b: Decimal, *, tolerance: Decimal = Decimal("0.05")) -> bool:
    if b == 0:
        return a == 0
    return abs(a - b) / abs(b) <= tolerance or abs(a - b) <= Decimal("1")