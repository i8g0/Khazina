#!/usr/bin/env python3
"""Generate Demo_Enterprise_Dataset_v2.xlsx — W-1 compatible, 20k+ rows (Sprint 7)."""

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

OUTPUT = Path(__file__).resolve().parent / "Demo_Enterprise_Dataset_v2.xlsx"
ROW_COUNT = 20_500
TOTAL_SPEND = 285_000_000
SEED = 20260717

DEPARTMENTS = [
    "الشؤون المالية",
    "المشتريات",
    "العمليات",
    "تقنية المعلومات",
    "الموارد البشرية",
    "التسويق",
    "اللوجستيات",
    "القانونية",
    "الامتثال",
    "المرافق",
    "المشاريع",
    "رأس المال",
]

CATEGORIES = [
    "finance",
    "procurement",
    "operations",
    "it",
    "hr",
    "marketing",
    "logistics",
    "legal",
    "compliance",
    "facilities",
    "overlapping_contracts",
    "travel",
]

SUPPLIERS = [f"مورد-{i:03d}" for i in range(1, 121)]

TRANSACTION_TYPES = [
    "invoice",
    "contract",
    "purchase_order",
    "travel",
    "payroll",
    "asset",
    "maintenance",
    "project",
    "capex",
    "opex",
    "tax",
    "subscription",
]

# Waste intensity weights per category (higher = more waste rows)
CATEGORY_WEIGHTS: dict[str, float] = {
    "finance": 2.8,
    "procurement": +2.2,
    "overlapping_contracts": 2.5,
    "operations": 1.4,
    "it": 1.8,
    "logistics": 1.3,
    "hr": 1.0,
    "marketing": 1.1,
    "legal": 0.9,
    "compliance": 1.2,
    "facilities": 0.8,
    "travel": 1.5,
}


def _weighted_category(rng: random.Random) -> str:
    keys = list(CATEGORY_WEIGHTS.keys())
    weights = [CATEGORY_WEIGHTS[k] for k in keys]
    return rng.choices(keys, weights=weights, k=1)[0]


TARGET_WASTE = 22_000_000  # ~7.7% of spend


def _amount_for_scenario(rng: random.Random, scenario: str) -> int:
    if scenario == "duplicate":
        return rng.randint(800, 12_000)
    if scenario == "overrun":
        return rng.randint(2_000, 18_000)
    if scenario == "subscription":
        return rng.randint(500, 6_000)
    if scenario == "late_payment":
        return rng.randint(1_000, 9_000)
    if scenario == "concentration":
        return rng.randint(5_000, 35_000)
    return rng.randint(200, 8_000)


def build_rows(rng: random.Random) -> list[dict]:
    rows: list[dict] = []
    duplicate_pool: list[dict] = []

    for i in range(ROW_COUNT):
        roll = rng.random()
        if roll < 0.03:
            scenario = "duplicate"
        elif roll < 0.08:
            scenario = "overrun"
        elif roll < 0.11:
            scenario = "subscription"
        elif roll < 0.14:
            scenario = "late_payment"
        elif roll < 0.18:
            scenario = "concentration"
        else:
            scenario = "normal"

        category = _weighted_category(rng)
        dept = rng.choice(DEPARTMENTS)
        supplier = rng.choices(
            SUPPLIERS,
            weights=[3.0 if s.endswith("001") or s.endswith("017") else 1.0 for s in SUPPLIERS],
            k=1,
        )[0]
        tx_type = rng.choice(TRANSACTION_TYPES)
        amount = _amount_for_scenario(rng, scenario)
        budget = int(amount * rng.uniform(0.75, 1.05))
        actual = amount if scenario != "overrun" else int(amount * rng.uniform(1.12, 1.35))

        row = {
            "category": category,
            "amount": amount,
            "total_spend": TOTAL_SPEND,
            "department": dept,
            "supplier": supplier,
            "transaction_type": tx_type,
            "planned_amount": budget,
            "spent_amount": actual,
        }
        rows.append(row)
        if scenario == "duplicate" and len(duplicate_pool) < 400:
            duplicate_pool.append(row)

    for dup in duplicate_pool[:200]:
        clone = dict(dup)
        clone["amount"] = dup["amount"]
        rows.append(clone)

    rng.shuffle(rows)
    rows = rows[:ROW_COUNT]
    total = sum(r["amount"] for r in rows)
    if total > 0:
        scale = TARGET_WASTE / total
        for row in rows:
            row["amount"] = max(100, int(row["amount"] * scale))
            row["planned_amount"] = max(100, int(row["planned_amount"] * scale))
            row["spent_amount"] = max(100, int(row["spent_amount"] * scale))
    return rows


def write_workbook(path: Path, rows: list[dict]) -> None:
    wb = Workbook()
    sheet = wb.active
    sheet.title = "FinancialWaste"
    headers = [
        "category",
        "amount",
        "total_spend",
        "department",
        "supplier",
        "transaction_type",
        "planned_amount",
        "spent_amount",
    ]
    sheet.append(headers)
    for row in rows:
        sheet.append([row[h] for h in headers])
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


def summarize(rows: list[dict]) -> dict:
    total_waste = sum(r["amount"] for r in rows)
    waste_pct = (Decimal(total_waste) / Decimal(TOTAL_SPEND) * 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    depts = len({r["department"] for r in rows})
    suppliers = len({r["supplier"] for r in rows})
    return {
        "row_count": len(rows),
        "departments": depts,
        "suppliers": suppliers,
        "total_waste": total_waste,
        "waste_pct": float(waste_pct),
    }


def main() -> int:
    rng = random.Random(SEED)
    rows = build_rows(rng)
    stats = summarize(rows)
    if stats["total_waste"] > TOTAL_SPEND:
        print("ERROR: waste exceeds spend", file=sys.stderr)
        return 1

    write_workbook(OUTPUT, rows)
    print(f"Wrote {OUTPUT}")
    print(
        f"  rows={stats['row_count']} depts={stats['departments']} "
        f"suppliers={stats['suppliers']}"
    )
    print(f"  total_waste={stats['total_waste']:,} ({stats['waste_pct']}% of spend)")

    local = validate_local(OUTPUT)
    if not local.get("accepted"):
        print(f"VALIDATION FAILED: {local}", file=sys.stderr)
        return 1
    print(f"  ingestion OK records={local['record_count']} quality={local['quality_score']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
