import type { ApiResponse } from "@/lib/api/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly errors: string[] | null = null,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function buildHeaders(token: string | null, body?: unknown): Headers {
  const headers = new Headers();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (body !== undefined && !(body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  return headers;
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit & {
    token?: string | null;
    /** When true, honor API contracts that return `data: null` on success. */
    allowNull?: boolean;
  } = {},
): Promise<T> {
  const { token = null, allowNull = false, ...init } = options;
  const response = await fetch(`${API_BASE}/api/v1${path}`, {
    ...init,
    headers: buildHeaders(token, init.body),
  });

  if (response.status === 401) {
    throw new ApiError(401, "يرجى تسجيل الدخول للمتابعة");
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/pdf")) {
    throw new ApiError(
      response.status,
      "تعذّر تحميل التقرير — أعد المحاولة",
    );
  }

  let envelope: ApiResponse<T>;
  try {
    envelope = (await response.json()) as ApiResponse<T>;
  } catch {
    throw new ApiError(response.status, "تعذّر قراءة الرد — أعد المحاولة");
  }

  if (!response.ok || !envelope.success) {
    throw new ApiError(
      response.status,
      envelope.message || "تعذّر إتمام الطلب",
      envelope.errors,
    );
  }

  if (envelope.data === null) {
    if (allowNull) {
      return null as T;
    }
    throw new ApiError(response.status, envelope.message || "لا توجد بيانات");
  }

  return envelope.data;
}

export async function downloadBinary(
  path: string,
  token: string,
): Promise<Blob> {
  const response = await fetch(`${API_BASE}/api/v1${path}`, {
    headers: buildHeaders(token),
  });
  if (response.status === 401) {
    throw new ApiError(401, "يرجى تسجيل الدخول للمتابعة");
  }
  if (!response.ok) {
    throw new ApiError(response.status, "فشل تنزيل الملف");
  }
  return response.blob();
}
