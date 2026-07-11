"use client";

import { Badge } from "@/components/ui/badge";
import type { SimulationScenario } from "@/lib/placeholder-data";
import { cn } from "@/lib/utils";

export interface SimulationScenarioCardProps {
  scenario: SimulationScenario;
  active: boolean;
  onSelect: () => void;
}

function statusVariant(status: string) {
  if (status === "مكتمل") {
    return "success" as const;
  }
  return "secondary" as const;
}

export function SimulationScenarioCard({
  scenario,
  active,
  onSelect,
}: SimulationScenarioCardProps) {
  return (
    <button
      type="button"
      role="option"
      aria-selected={active}
      onClick={onSelect}
      className={cn(
        "flex h-full min-h-[140px] w-full flex-col rounded-2xl border bg-surface px-5 py-5 text-start transition-colors md:min-h-[152px] md:px-6 md:py-6",
        active
          ? "border-gold-primary shadow-[0_0_0_1px_rgba(184,137,45,0.35)]"
          : "border-border/60 hover:border-gold-primary/25",
      )}
    >
      <div className="mb-4 flex items-start justify-between gap-3">
        <Badge
          variant={statusVariant(scenario.status)}
          className="px-3 py-1 text-xs font-semibold"
        >
          {scenario.status}
        </Badge>
      </div>
      <h3 className="mb-1.5 text-base font-semibold leading-snug tracking-tight text-black-primary md:text-lg">
        {scenario.name}
      </h3>
      <p className="flex-1 text-sm leading-7 text-muted md:text-[15px]">
        {scenario.description}
      </p>
    </button>
  );
}
