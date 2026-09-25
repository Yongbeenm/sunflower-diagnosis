import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { act, renderHook } from "@testing-library/react";
import { AuthProvider, useAuth } from "../context";
import * as authApi from "../api";
import type { User } from "../types";

vi.mock("../api", () => ({
  loginApi: vi.fn(),
  registerApi: vi.fn(),
  refreshApi: vi.fn(),
  logoutApi: vi.fn(),
  updateMeApi: vi.fn(),
}));

describe("AuthProvider Session Persistence", () => {
  const mockUser: User = {
    id: 1,
    email: "admin@example.com",
    username: "admin",
    role: "admin",
    permissions: ["disease:read", "analytics:read"],
    is_active: true,
  };

  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it("restores user and accessToken from localStorage immediately on mount", async () => {
    localStorage.setItem("sunflower_auth_user", JSON.stringify(mockUser));
    localStorage.setItem("sunflower_access_token", "saved-access-token");

    vi.mocked(authApi.refreshApi).mockResolvedValueOnce({
      access_token: "refreshed-token",
      token_type: "bearer",
      user: { ...mockUser, username: "admin_refreshed" },
    });

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    let hookResult: any;
    await act(async () => {
      const { result } = renderHook(() => useAuth(), { wrapper });
      hookResult = result;
    });

    // Instantly available without waiting for background refresh
    expect(hookResult.current.isAuthenticated).toBe(true);
    expect(hookResult.current.user?.username).toBe("admin_refreshed");
    expect(hookResult.current.accessToken).toBe("refreshed-token");
    expect(hookResult.current.isLoading).toBe(false);
  });

  it("saves session to localStorage on successful login", async () => {
    vi.mocked(authApi.refreshApi).mockRejectedValueOnce(new Error("No cookie"));
    vi.mocked(authApi.loginApi).mockResolvedValueOnce({
      access_token: "new-login-token",
      token_type: "bearer",
      user: mockUser,
    });

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.login({ identifier: "admin", password: "password123" });
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user?.email).toBe("admin@example.com");
    expect(localStorage.getItem("sunflower_access_token")).toBe("new-login-token");
    expect(JSON.parse(localStorage.getItem("sunflower_auth_user") || "{}")).toEqual(mockUser);
  });

  it("clears session from localStorage on logout", async () => {
    localStorage.setItem("sunflower_auth_user", JSON.stringify(mockUser));
    localStorage.setItem("sunflower_access_token", "saved-token");

    vi.mocked(authApi.refreshApi).mockResolvedValueOnce({
      access_token: "saved-token",
      token_type: "bearer",
      user: mockUser,
    });
    vi.mocked(authApi.logoutApi).mockResolvedValueOnce(undefined);

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(localStorage.getItem("sunflower_auth_user")).toBeNull();
    expect(localStorage.getItem("sunflower_access_token")).toBeNull();
  });
});
