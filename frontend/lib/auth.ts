const TOKEN_KEY = "tenantmng.access_token";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setAccessToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken());
}

export function readAccessTokenClaims(): {
  sub?: string;
  email?: string;
  is_superuser?: boolean;
} | null {
  const token = getAccessToken();
  if (!token) {
    return null;
  }
  const segment = token.split(".")[1];
  if (!segment) {
    return null;
  }
  try {
    const padded = segment.replace(/-/g, "+").replace(/_/g, "/");
    const json = atob(
      padded.padEnd(padded.length + ((4 - (padded.length % 4)) % 4), "="),
    );
    return JSON.parse(json) as {
      sub?: string;
      email?: string;
      is_superuser?: boolean;
    };
  } catch {
    return null;
  }
}

export function safeNextPath(value: string | null): string {
  if (value && value.startsWith("/") && !value.startsWith("//")) {
    return value;
  }
  return "/dashboard";
}
