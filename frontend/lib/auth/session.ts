const TOKEN_KEY = "khazina_token";
const ORG_ID_KEY = "khazina_org_id";
const EMAIL_KEY = "khazina_email";

export interface SessionSnapshot {
  token: string;
  organizationId: string;
  email: string;
}

export function readSession(): SessionSnapshot | null {
  if (typeof window === "undefined") {
    return null;
  }
  const token = window.localStorage.getItem(TOKEN_KEY);
  const organizationId = window.localStorage.getItem(ORG_ID_KEY);
  const email = window.localStorage.getItem(EMAIL_KEY);
  if (!token || !organizationId || !email) {
    return null;
  }
  return { token, organizationId, email };
}

export function writeSession(session: SessionSnapshot): void {
  window.localStorage.setItem(TOKEN_KEY, session.token);
  window.localStorage.setItem(ORG_ID_KEY, session.organizationId);
  window.localStorage.setItem(EMAIL_KEY, session.email);
}

export function clearSession(): void {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(ORG_ID_KEY);
  window.localStorage.removeItem(EMAIL_KEY);
}
