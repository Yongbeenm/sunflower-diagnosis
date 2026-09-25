import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { ProfilePage } from "../pages/ProfilePage";
import * as AuthContextModule from "../context";
import "@/i18n";

describe("ProfilePage", () => {
  const mockUpdateProfile = vi.fn();
  const mockUser = {
    id: 1,
    email: "admin@example.com",
    username: "admin",
    role: "admin",
    permissions: ["disease:read", "disease:write", "analytics:read"],
    is_active: true,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(AuthContextModule, "useAuth").mockReturnValue({
      user: mockUser,
      accessToken: "fake-jwt",
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      updateProfile: mockUpdateProfile,
      logout: vi.fn(),
      refreshSession: vi.fn(),
      hasPermission: (perm: string) => mockUser.permissions.includes(perm),
    });
  });

  it("renders profile header and overview tabs correctly", () => {
    render(
      <MemoryRouter>
        <ProfilePage />
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "admin" })).toBeInTheDocument();
    expect(screen.getAllByText("admin@example.com").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/Active/i)).toBeInTheDocument();
    expect(screen.getByText(/Account ID/i)).toBeInTheDocument();
    expect(screen.getByText(/Granted Permissions/i)).toBeInTheDocument();
  });

  it("switches to Edit Details tab and allows updating account info", async () => {
    mockUpdateProfile.mockResolvedValueOnce({
      ...mockUser,
      username: "admin_updated",
    });

    render(
      <MemoryRouter>
        <ProfilePage />
      </MemoryRouter>,
    );

    // Switch to edit details tab
    fireEvent.click(screen.getByRole("button", { name: /Edit Details/i }));

    expect(screen.getByText(/Edit Account Details/i)).toBeInTheDocument();

    const usernameInput = screen.getByLabelText(/Username/i);
    const currentPassInput = screen.getByLabelText(/Current Password/i);

    fireEvent.change(usernameInput, { target: { value: "admin_updated" } });
    fireEvent.change(currentPassInput, { target: { value: "secret123" } });

    fireEvent.click(screen.getByRole("button", { name: /^Save$/i }));

    await waitFor(() => {
      expect(mockUpdateProfile).toHaveBeenCalledWith({
        username: "admin_updated",
        current_password: "secret123",
      });
    });
  });

  it("switches to Security tab and validates password mismatch", async () => {
    render(
      <MemoryRouter>
        <ProfilePage />
      </MemoryRouter>,
    );

    // Switch to security tab
    fireEvent.click(screen.getByRole("button", { name: /Security/i }));

    expect(screen.getByText(/Change Password/i)).toBeInTheDocument();

    const currentPassInput = screen.getByLabelText(/Current Password/i);
    const newPassInput = screen.getByLabelText(/^New Password/i);
    const confirmPassInput = screen.getByLabelText(/Confirm New Password/i);

    fireEvent.change(currentPassInput, { target: { value: "secret123" } });
    fireEvent.change(newPassInput, { target: { value: "newsecret123" } });
    fireEvent.change(confirmPassInput, { target: { value: "different123" } });

    fireEvent.click(screen.getByRole("button", { name: /Update Password/i }));

    await waitFor(() => {
      expect(screen.getByText(/New password and confirmation do not match/i)).toBeInTheDocument();
    });

    expect(mockUpdateProfile).not.toHaveBeenCalled();
  });
});
