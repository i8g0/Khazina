"use client";

import { AppProviders } from "@/components/providers/app-providers";
import { TooltipProvider } from "@/components/providers/tooltip-provider";

export function RootProviders({ children }: { children: React.ReactNode }) {
  return (
    <AppProviders>
      <TooltipProvider>{children}</TooltipProvider>
    </AppProviders>
  );
}
