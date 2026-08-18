import { clearAccessToken, getAccessToken } from "@/lib/auth";
import type { ApiError } from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  auth?: boolean;
};

function formatDetail(detail: ApiError["detail"] | undefined): string {
  if (!detail) {
    return "Request failed";
  }
  if (typeof detail === "string") {
    return detail;
  }
  return detail
    .map((item) => (typeof item === "string" ? item : item.msg ?? "Invalid value"))
    .join("; ");
}

export async function api<T>(
  path: string,
  { body, auth = true, headers, ...init }: RequestOptions = {},
): Promise<T> {
  const token = auth ? getAccessToken() : null;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (response.status === 401 && auth) {
    clearAccessToken();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const payload = (await response.json()) as ApiError;
      detail = formatDetail(payload.detail);
    } catch {
      // keep status text
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
