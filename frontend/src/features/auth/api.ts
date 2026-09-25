import { apiFetch } from "@/api/client";
import type { LoginCredentials, RegisterCredentials, TokenResponse, User } from "./types";

export async function loginApi(credentials: LoginCredentials): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
}

export async function registerApi(credentials: RegisterCredentials): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
}

export async function refreshApi(): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/auth/refresh", {
    method: "POST",
  });
}

export async function logoutApi(): Promise<void> {
  await apiFetch<undefined>("/auth/logout", {
    method: "POST",
  });
}

export async function getMeApi(): Promise<User> {
  return apiFetch<User>("/auth/me", {
    method: "GET",
  });
}

export async function updateMeApi(credentials: import("./types").UpdateMeCredentials): Promise<User> {
  return apiFetch<User>("/users/me", {
    method: "PATCH",
    body: JSON.stringify(credentials),
  });
}

