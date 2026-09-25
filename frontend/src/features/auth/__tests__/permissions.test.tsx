import React from "react";
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { AuthContext, RequirePermission } from "../context";
import type { User } from "../types";

function renderWithAuth(
  ui: React.ReactElement,
  authValues: {
    user: User | null;
    accessToken: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
  },
) {
  return render(
    <AuthContext.Provider
      value={{
        ...authValues,
        login: vi.fn(),
        register: vi.fn(),
        updateProfile: vi.fn(),
        logout: vi.fn(),
        refreshSession: vi.fn(),
        hasPermission: (code: string) => !!authValues.user?.permissions?.includes(code),
      }}
    >
      {ui}
    </AuthContext.Provider>,
  );
}

describe("RequirePermission component", () => {
  it("renders children when user has required permission", () => {
    renderWithAuth(
      <RequirePermission code="disease:create" fallback={<div>Access Denied</div>}>
        <div>Protected Content</div>
      </RequirePermission>,
      {
        user: {
          id: 1,
          email: "admin@example.com",
          username: "admin",
          role: "admin",
          permissions: ["disease:create", "disease:read"],
          is_active: true,
        },
        accessToken: "mock-token",
        isAuthenticated: true,
        isLoading: false,
      },
    );

    expect(screen.getByText("Protected Content")).toBeInTheDocument();
    expect(screen.queryByText("Access Denied")).not.toBeInTheDocument();
  });

  it("renders fallback when user lacks required permission", () => {
    renderWithAuth(
      <RequirePermission code="disease:create" fallback={<div>Access Denied</div>}>
        <div>Protected Content</div>
      </RequirePermission>,
      {
        user: {
          id: 2,
          email: "grower@example.com",
          username: "grower",
          role: "grower",
          permissions: ["disease:read"],
          is_active: true,
        },
        accessToken: "mock-token",
        isAuthenticated: true,
        isLoading: false,
      },
    );

    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    expect(screen.getByText("Access Denied")).toBeInTheDocument();
  });

  it("renders fallback when user is unauthenticated", () => {
    renderWithAuth(
      <RequirePermission code="disease:create" fallback={<div>Please Sign In</div>}>
        <div>Protected Content</div>
      </RequirePermission>,
      {
        user: null,
        accessToken: null,
        isAuthenticated: false,
        isLoading: false,
      },
    );

    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    expect(screen.getByText("Please Sign In")).toBeInTheDocument();
  });

  it("renders null while authentication state is loading", () => {
    const { container } = renderWithAuth(
      <RequirePermission code="disease:create" fallback={<div>Access Denied</div>}>
        <div>Protected Content</div>
      </RequirePermission>,
      {
        user: null,
        accessToken: null,
        isAuthenticated: false,
        isLoading: true,
      },
    );

    expect(container.firstChild).toBeNull();
  });
});
