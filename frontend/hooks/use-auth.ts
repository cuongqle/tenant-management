import { api } from "@/lib/api";
import { setAccessToken } from "@/lib/auth";
import type { LoginRequest, RegisterRequest, TokenResponse } from "@/types";

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  const token = await api<TokenResponse>("/api/v1/auth/login", {
    method: "POST",
    body: payload,
    auth: false,
  });
  setAccessToken(token.access_token);
  return token;
}

export async function register(payload: RegisterRequest): Promise<TokenResponse> {
  const token = await api<TokenResponse>("/api/v1/auth/register", {
    method: "POST",
    body: payload,
    auth: false,
  });
  setAccessToken(token.access_token);
  return token;
}
