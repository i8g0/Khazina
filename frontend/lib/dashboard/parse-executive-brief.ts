import { sanitizeExecutiveText } from "@/lib/format";

export interface ExecutiveBriefSection {
  id: string;
  label: string;
  body: string;
}

/** Canonical board narrative order from the Arabic executive-summary prompt. */
const BRIEF_SECTION_DEFS: Array<{ id: string; label: string }> = [
  { id: "situation", label: "الوضع" },
  { id: "problem", label: "المشكلة" },
  { id: "business-risks", label: "المخاطر على الأعمال" },
  { id: "opportunity", label: "الفرصة" },
  { id: "expected-value", label: "القيمة المتوقعة" },
  { id: "required-decision", label: "القرار المطلوب" },
  { id: "executive-judgment", label: "الحكم التنفيذي" },
];

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Splits an AI executive narrative into labeled sections a CFO can scan.
 * Works for both newline-separated and single-line "Label: … Label: …" forms.
 */
export function parseExecutiveBriefSections(text: string): ExecutiveBriefSection[] {
  const cleaned = sanitizeExecutiveText(text);
  if (!cleaned.trim()) return [];

  const labelAlternation = BRIEF_SECTION_DEFS.map((d) => escapeRegExp(d.label)).join("|");
  const splitter = new RegExp(`(?:^|[\\s.])(${labelAlternation})\\s*:\\s*`, "gu");

  const matches = [...cleaned.matchAll(splitter)];
  if (matches.length === 0) {
    return [
      {
        id: "narrative",
        label: "الملخص",
        body: cleaned,
      },
    ];
  }

  const sections: ExecutiveBriefSection[] = [];
  for (let i = 0; i < matches.length; i += 1) {
    const match = matches[i];
    const label = match[1];
    const def = BRIEF_SECTION_DEFS.find((d) => d.label === label);
    const start = (match.index ?? 0) + match[0].length;
    const end =
      i + 1 < matches.length ? (matches[i + 1].index ?? cleaned.length) : cleaned.length;
    const body = cleaned.slice(start, end).replace(/^[.\s]+|[.\s]+$/g, "").trim();
    if (!body) continue;
    sections.push({
      id: def?.id ?? `section-${i}`,
      label: def?.label ?? label,
      body,
    });
  }

  return sections;
}

/** Prefer waste narrative (structured board format); fall back to concatenated parts. */
export function buildPrimaryBriefNarrative(
  parts: { domain: string; text: string }[],
): string | null {
  const waste = parts.find((p) => p.domain === "الهدر");
  if (waste?.text.trim()) return waste.text.trim();
  if (parts.length === 0) return null;
  return parts.map((p) => p.text.trim()).filter(Boolean).join("\n\n");
}
