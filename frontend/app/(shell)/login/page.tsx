"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert } from "@/components/ui/alert";
import { useAuth, formatApiError, isDemoAutologinEnabled } from "@/lib/auth/auth-context";
import { AuthLoadingShell } from "@/components/workflow/auth-loading-shell";
import { SITE_NAME } from "@/app/site";

export default function LoginPage() {
  const router = useRouter();
  const { session, isLoading, signIn } = useAuth();
  const [email, setEmail] = React.useState("demo@khazina.sa");
  const [password, setPassword] = React.useState("DemoExec2026!");
  const [submitting, setSubmitting] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (isLoading) return;
    if (session) {
      router.replace("/");
    }
  }, [isLoading, session, router]);

  if (isLoading || isDemoAutologinEnabled()) {
    return <AuthLoadingShell />;
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await signIn(email, password);
      router.replace("/");
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-bg-light px-4">
      <div className="w-full max-w-md rounded-2xl border border-border/70 bg-surface p-8 shadow-sm">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold text-foreground">{SITE_NAME}</h1>
          <p className="mt-2 text-sm text-muted">تسجيل الدخول إلى المنصة التنفيذية</p>
        </div>

        {error ? (
          <Alert variant="destructive" title="تعذّر تسجيل الدخول" className="mb-4">
            {error}
          </Alert>
        ) : null}

        <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium">البريد الإلكتروني</label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              dir="ltr"
            />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium">كلمة المرور</label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              dir="ltr"
            />
          </div>
          <Button type="submit" className="w-full" disabled={submitting}>
            {submitting ? "جاري الدخول..." : "دخول"}
          </Button>
        </form>
      </div>
    </div>
  );
}
