const TOKEN_KEY = "khazina_token";
const ORG_ID_KEY = "khazina_org_id";
const EMAIL_KEY = "khazina_email";
const ORG_NAME_KEY = "khazina_org_name";
const ORG_PLATFORM_KEY = "khazina_org_platform";
const ORG_EXEC_KEY = "khazina_org_exec";

export interface SessionSnapshot {
  token: string;
  organizationId: string;
  email: string;
  organizationName: string;
  platformName: string;
  executiveTitle: string | null;
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
  return {
    token,
    organizationId,
    email,
    organizationName: window.localStorage.getItem(ORG_NAME_KEY) ?? "",
    platformName: window.localStorage.getItem(ORG_PLATFORM_KEY) ?? "خزينة",
    executiveTitle: window.localStorage.getItem(ORG_EXEC_KEY),
  };
}

export function writeSession(session: SessionSnapshot): void {
  window.localStorage.setItem(TOKEN_KEY, session.token);
  window.localStorage.setItem(ORG_ID_KEY, session.organizationId);
  window.localStorage.setItem(EMAIL_KEY, session.email);
  window.localStorage.setItem(ORG_NAME_KEY, session.organizationName);
  window.localStorage.setItem(ORG_PLATFORM_KEY, session.platformName);
  if (session.executiveTitle) {
    window.localStorage.setItem(ORG_EXEC_KEY, session.executiveTitle);
  } else {
    window.localStorage.removeItem(ORG_EXEC_KEY);
  }
}

export function clearSession(): void {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(ORG_ID_KEY);
  window.localStorage.removeItem(EMAIL_KEY);
  window.localStorage.removeItem(ORG_NAME_KEY);
  window.localStorage.removeItem(ORG_PLATFORM_KEY);
  window.localStorage.removeItem(ORG_EXEC_KEY);
}
