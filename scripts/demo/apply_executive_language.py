#!/usr/bin/env python3
"""Apply executive language patches to ar.py prompts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AR_PY = ROOT / "backend" / "app" / "ai" / "prompts" / "languages" / "ar.py"

RISK_OLD_START = "        PromptTask.RISK_MITIGATION_OPTIONS:"
RISK_NEW = '''        PromptTask.RISK_MITIGATION_OPTIONS: """\\
## المهمة: قرارات تخفيف المخاطر لمجلس الإدارة

قدّم خمس قرارات تنفيذية لتخفيف المخاطر المالية — مرتبطة بنتائج التحليل فقط.

### تنسيق كل توصية (إلزامي)

1.
الزاوية التنفيذية:
[إجراءات فورية | مراقبة | ضوابط مالية | ضوابط تشغيلية | حوكمة | امتثال]
المشكلة:
[ما الخطر التجاري — جملتان]
الدليل:
المخاطرة: [من السياق]
الفترة: [من السياق]
الدرجة: [من السياق]
الأثر المالي: [من السياق]
لماذا الأولوية:
[لماذا الآن]
القرار:
[قرار تنفيذي محدد]
الأثر على الأعمال:
[الأثر على الربحية أو السيولة أو الحوكمة]
الأولوية:
[عالية | متوسطة | منخفضة]
المسؤول:
[من السياق أو «غير متوفر في البيانات الحالية»]
الإطار الزمني:
[30–45 يوماً | 60–90 يوماً]
النتيجة المتوقعة:
[أرقام من السياق فقط أو «غير متوفر في البيانات الحالية»]
مؤشر النجاح:
[مؤشر قابل للقياس]

ثم 2. و 3. و 4. و 5. بنفس الهيكل.
""",'''


def main() -> None:
    text = AR_PY.read_text(encoding="utf-8")
    text = text.replace("(Sprint 4)", "")
    text = text.replace("CEO/CFO", "الرئيس التنفيذي أو المدير المالي")
    text = text.replace("[KPI قابل للقياس]", "[مؤشر أداء قابل للقياس]")
    for tag in (
        "(Risk Executive Summary)",
        "(Risk Executive Brief)",
        "(Risk Explanation)",
        "(Risk Mitigation Options)",
        "(Risk Board Report)",
    ):
        text = text.replace(tag, "")

    start = text.find(RISK_OLD_START)
    if start == -1:
        raise SystemExit("RISK_MITIGATION block not found")
    end = text.find('        PromptTask.RISK_BOARD_REPORT:', start)
    if end == -1:
        raise SystemExit("RISK_BOARD end not found")
    text = text[:start] + RISK_NEW + "\n" + text[end:]
    AR_PY.write_text(text, encoding="utf-8")
    print("Updated", AR_PY)


if __name__ == "__main__":
    main()
