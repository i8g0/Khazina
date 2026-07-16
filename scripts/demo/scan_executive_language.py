#!/usr/bin/env python3
"""Scan user-visible strings for forbidden technical vocabulary."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN = [
    r"\bJSON\b",
    r"\bUUID\b",
    r"\bsnapshot\b",
    r"\banalysis_run\b",
    r"\bmetadata\b",
    r"\bfacts_contract\b",
    r"\bSprint\s+\d+",
    r"Internal Server Error",
    r"Validation Error",
    r"الذكاء الاصطناعي",
    r"محرك",
    r"مستودع البيانات",
    r"\bKPIs?\b",
    r"\bAI\b",
    r"CEO/CFO",
    r"Facts Contract",
]

SCAN_DIRS = [
    ROOT / "frontend" / "components",
    ROOT / "frontend" / "lib" / "workflow",
    ROOT / "frontend" / "lib" / "placeholder-data.ts",
]

SKIP_PARTS = {"node_modules", ".next", "khazina-api.ts", "types.ts", "demo"}


def main() -> int:
    hits: list[str] = []
    for base in SCAN_DIRS:
        paths = [base] if base.is_file() else base.rglob("*")
        for path in paths:
            if not path.is_file() or path.suffix not in {".tsx", ".ts"}:
                continue
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for pattern in FORBIDDEN:
                    if re.search(pattern, line, re.I):
                        hits.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()[:120]}")
                        break
    out = ROOT / "scripts" / "demo" / "executive_language_scan.txt"
    out.write_text("\n".join(hits) if hits else "CLEAN — no forbidden terms in scanned UI paths", encoding="utf-8")
    print(f"Hits: {len(hits)} — report: {out}")
    for h in hits[:30]:
        print(h)
    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
