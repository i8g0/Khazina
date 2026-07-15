"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { ApiError } from "@/lib/api/client";
import { getActiveOrganization, login } from "@/lib/api/khazina-api";
import {
  clearSession,
  readSession,
  writeSession,
  type SessionSnapshot,
} from "@/lib/auth/session";
import { clearDemoArtifacts } from "@/lib/demo/state";

interface AuthContextValue {
  session: SessionSnapshot | null;
  isLoading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => void;
  updateSession: (partial: Partial<SessionSnapshot>) => void;
}

const AuthContext = React.createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = React.useState<SessionSnapshot | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    setSession(readSession());
    setIsLoading(false);
  }, []);

  const signIn = React.useCallback(async (email: string, password: string) => {
    const tokenResponse = await login(email, password);
    const org = await getActiveOrganization(tokenResponse.access_token);
    const snapshot: SessionSnapshot = {
      token: tokenResponse.access_token,
      organizationId: org.id,
      email: email.trim().toLowerCase(),
      organizationName: org.name,
      platformName: org.platform_name,
      executiveTitle: org.executive_title,
    };
    writeSession(snapshot);
    setSession(snapshot);
  }, []);

  const signOut = React.useCallback(() => {
    clearSession();
    clearDemoArtifacts();
    setSession(null);
  }, []);

  const updateSession = React.useCallback((partial: Partial<SessionSnapshot>) => {
    setSession((current) => {
      if (!current) return current;
      const next = { ...current, ...partial };
      writeSession(next);
      return next;
    });
  }, []);

  return (
    <AuthContext.Provider
      value={{ session, isLoading, signIn, signOut, updateSession }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const value = React.useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return value;
}

export function useRequireAuth(): AuthContextValue {
  const auth = useAuth();
  const router = useRouter();

  React.useEffect(() => {
    if (!auth.isLoading && !auth.session) {
      router.replace("/login");
    }
  }, [auth.isLoading, auth.session, router]);

  return auth;
}

/** Display helpers from live session (falls back only for optional fields). */
export function useOrganizationDisplay() {
  const { session } = useAuth();
  return {
    name: session?.organizationName || "—",
    platformName: session?.platformName || "خزينة",
    executiveTitle: session?.executiveTitle || "المستخدم التنفيذي",
    /** No backend field for reporting period label — UI period badge only. */
    reportingPeriod: "الفترة النشطة",
  };
}

export function formatApiError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return "انتهت صلاحية الجلسة أو غير مصرح — سجّل الدخول مجدداً";
    }
    if (error.status === 403) {
      return "ليس لديك صلاحية لتنفيذ هذا الإجراء";
    }
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "حدث خطأ غير متوقع";
}
