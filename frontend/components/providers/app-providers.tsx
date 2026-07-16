"use client";

import { AuthProvider } from "@/lib/auth/auth-context";
import { OrgLookupsProvider } from "@/lib/org-lookups";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <OrgLookupsProvider>{children}</OrgLookupsProvider>
    </AuthProvider>
  );
}
