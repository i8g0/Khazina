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

interface AuthContextValue {
  session: SessionSnapshot | null;
  isLoading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => void;
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
    };
    writeSession(snapshot);
    setSession(snapshot);
  }, []);

  const signOut = React.useCallback(() => {
    clearSession();
    setSession(null);
  }, []);

  return (
    <AuthContext.Provider value={{ session, isLoading, signIn, signOut }}>
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

export function formatApiError(error: unknown): string {
  if (error instanceof ApiError) {
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
