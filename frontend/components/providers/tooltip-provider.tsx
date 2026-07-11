"use client";

import { TooltipProvider as RadixTooltipProvider } from "@radix-ui/react-tooltip";

export function TooltipProvider({ children }: { children: React.ReactNode }) {
  return (
    <RadixTooltipProvider delayDuration={200}>{children}</RadixTooltipProvider>
  );
}
