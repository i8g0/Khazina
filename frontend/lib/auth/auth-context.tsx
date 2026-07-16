"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { humanizeErrorMessage } from "@/lib/workflow/messages";
import { stripTechnicalLanguage } from "@/lib/executive-language";
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

/** Local/dev auto-login — skip the login page when no session is stored. */
const DEV_AUTO_LOGIN_EMAIL = "demo@khazina.sa";
const DEV_AUTO_LOGIN_PASSWORD = "DemoExec2026!";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = React.useState<SessionSnapshot | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

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

  React.useEffect(() => {
    let cancelled = false;

    async function hydrateSession() {
      const existing = readSession();
      if (existing) {
        try {
          await getActiveOrganization(existing.token);
          if (!cancelled) {
            setSession(existing);
            setIsLoading(false);
          }
          return;
        } catch {
          clearSession();
        }
      }

      try {
        const tokenResponse = await login(
          DEV_AUTO_LOGIN_EMAIL,
          DEV_AUTO_LOGIN_PASSWORD,
        );
        const org = await getActiveOrganization(tokenResponse.access_token);
        const snapshot: SessionSnapshot = {
          token: tokenResponse.access_token,
          organizationId: org.id,
          email: DEV_AUTO_LOGIN_EMAIL,
          organizationName: org.name,
          platformName: org.platform_name,
          executiveTitle: org.executive_title,
        };
        writeSession(snapshot);
        if (!cancelled) {
          setSession(snapshot);
        }
      } catch {
        if (!cancelled) {
          setSession(null);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void hydrateSession();
    return () => {
      cancelled = true;
    };
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

export { useOrganizationDisplay } from "@/lib/org-lookups";

export function formatApiError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return "انتهت صلاحية الجلسة — يرجى تسجيل الدخول مجدداً";
    }
    if (error.status === 403) {
      return "ليس لديك صلاحية لتنفيذ هذا الإجراء";
    }
    if (error.status === 503) {
      return "الخدمة غير متاحة مؤقتاً. أعد المحاولة بعد قليل.";
    }
    if (error.status >= 500) {
      return humanizeErrorMessage(
        error.message || "تعذّر إتمام العملية. أعد المحاولة بعد قليل.",
      );
    }
    return stripTechnicalLanguage(humanizeErrorMessage(error.message));
  }
  if (error instanceof Error) {
    return stripTechnicalLanguage(humanizeErrorMessage(error.message));
  }
  return "حدث خطأ غير متوقع. حاول مجدداً.";
}
