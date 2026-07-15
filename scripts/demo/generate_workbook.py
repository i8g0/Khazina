#!/usr/bin/env python3
"""Generate canonical Procurement_Q2.xlsx for hackathon demo."""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

OUTPUT = Path(__file__).resolve().parent / "Procurement_Q2.xlsx"

ROWS = [
    ("overlapping_contracts", 745_000, 50_000_000),
    ("operations", 520_000, 50_000_000),
    ("finance", 1_075_000, 50_000_000),
]


def main() -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "WasteData"
    sheet.append(["category", "amount", "total_spend"])
    for category, amount, total_spend in ROWS:
        sheet.append([category, amount, total_spend])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
