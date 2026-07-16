#!/usr/bin/env python3
"""Generate Khazina_Demo_Dataset_v2.xlsx — W-1 compatible enterprise waste workbook."""

from __future__ import annotations

import random
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from openpyxl import Workbook

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.ingestion.orchestrator import IngestionOrchestrator  # noqa: E402
from app.ingestion.exceptions import ValidationFailure, ParseError  # noqa: E402

OUTPUT = Path(__file__).resolve().parent / "Khazina_Demo_Dataset_v2.xlsx"
TOTAL_SPEND = 78_500_000
ROW_COUNT = 420
SEED = 20260717

# NovaTech Gulf — category-level waste buckets (W-1 schema: category, amount, total_spend).
# Rows aggregate by category; many rows simulate transaction-level granularity at ingest.
CATEGORY_TARGETS: dict[str, int] = {
    "finance": 2_088_000,  # overspend / concentration driver (~36% of waste)
    "procurement": 620_000,
    "overlapping_contracts": 620_000,  # duplicate vendor contracts
    "operations": 460_000,
    "it": 400_000,  # cloud / license spike
    "logistics": 320_000,
    "hr": 290_000,
    "legal": 250_000,
    "travel": 220_000,
    "marketing": 180_000,
    "compliance": 160_000,
    "administration": 130_000,
    "facilities": 110_000,
    "utilities": 112_000,
}


def _split_target(total: int, parts: int, rng: random.Random) -> list[int]:
    """Split *total* into *parts* positive integers with realistic variance."""
    if parts <= 0:
        return []
    if parts == 1:
        return [total]
    weights = [rng.uniform(0.4, 2.2) for _ in range(parts)]
    weight_sum = sum(weights)
    raw = [max(500, int(total * w / weight_sum)) for w in weights]
    diff = total - sum(raw)
    idx = 0
    while diff != 0:
        i = idx % parts
        step = 1 if diff > 0 else -1
        if raw[i] + step >= 500:
            raw[i] += step
            diff -= step
        idx += 1
        if idx > parts * abs(total) + 10_000:
            raise RuntimeError("Could not reconcile split amounts")
    return raw


def build_rows(rng: random.Random) -> list[tuple[str, int, int]]:
    categories = list(CATEGORY_TARGETS.keys())
    per_category = ROW_COUNT // len(categories)
    remainder = ROW_COUNT % len(categories)
    rows: list[tuple[str, int, int]] = []

    for index, category in enumerate(categories):
        count = per_category + (1 if index < remainder else 0)
        amounts = _split_target(CATEGORY_TARGETS[category], count, rng)
        for amount in amounts:
            rows.append((category, amount, TOTAL_SPEND))

    rng.shuffle(rows)
    return rows


def write_workbook(path: Path, rows: list[tuple[str, int, int]]) -> None:
    wb = Workbook()
    sheet = wb.active
    sheet.title = "FinancialWaste"
    sheet.append(["category", "amount", "total_spend"])
    for category, amount, total_spend in rows:
        sheet.append([category, amount, total_spend])
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def validate_local(path: Path) -> dict:
    orchestrator = IngestionOrchestrator()
    try:
        result = orchestrator.run(str(path), path.name)
        return {
            "accepted": True,
            "record_count": result.record_count,
            "quality_score": result.quality.overall_score,
        }
    except (ValidationFailure, ParseError) as exc:
        return {"accepted": False, "error": str(exc)}


def summarize(rows: list[tuple[str, int, int]]) -> dict:
    totals: dict[str, int] = {}
    for category, amount, _ in rows:
        totals[category] = totals.get(category, 0) + amount
    total_waste = sum(totals.values())
    top_cat = max(totals, key=totals.get)
    top_amt = totals[top_cat]
    pct = (Decimal(top_amt) / Decimal(total_waste) * 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    waste_pct = (Decimal(total_waste) / Decimal(TOTAL_SPEND) * 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return {
        "row_count": len(rows),
        "category_count": len(totals),
        "total_waste": total_waste,
        "waste_pct": float(waste_pct),
        "top_category": top_cat,
        "top_share_pct": float(pct),
        "totals_by_category": totals,
    }


def main() -> int:
    rng = random.Random(SEED)
    rows = build_rows(rng)
    stats = summarize(rows)
    if stats["total_waste"] > TOTAL_SPEND:
        print("ERROR: total waste exceeds total spend", file=sys.stderr)
        return 1

    write_workbook(OUTPUT, rows)
    print(f"Wrote {OUTPUT}")
    print(f"  rows={stats['row_count']} categories={stats['category_count']}")
    print(f"  total_waste={stats['total_waste']:,} ({stats['waste_pct']}% of spend)")
    print(f"  top={stats['top_category']} ({stats['top_share_pct']}% of waste)")

    local = validate_local(OUTPUT)
    if not local.get("accepted"):
        print(f"LOCAL VALIDATION FAILED: {local}", file=sys.stderr)
        return 1
    print(f"  local ingestion: OK (records={local['record_count']}, quality={local['quality_score']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
