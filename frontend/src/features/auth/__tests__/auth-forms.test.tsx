import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { LoginPage } from "../pages/LoginPage";
import { RegisterPage } from "../pages/RegisterPage";
import * as AuthContextModule from "../context";
import "@/i18n"; // Ensure i18n is initialized for tests

describe("Auth Forms", () => {
  const mockLogin = vi.fn();
  const mockRegister = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(AuthContextModule, "useAuth").mockReturnValue({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: false,
      login: mockLogin,
      register: mockRegister,
      updateProfile: vi.fn(),
      logout: vi.fn(),
      refreshSession: vi.fn(),
      hasPermission: vi.fn().mockReturnValue(false),
    });
  });

  describe("LoginPage", () => {
    it("renders login form elements correctly", () => {
      render(
        <MemoryRouter>
          <LoginPage />
        </MemoryRouter>,
      );

      expect(screen.getByLabelText(/Username or Email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /Sign In/i })).toBeInTheDocument();
      expect(screen.getByText(/Don't have an account\?/i)).toBeInTheDocument();
    });

    it("displays validation error when submitting empty fields", async () => {
      render(
        <MemoryRouter>
          <LoginPage />
        </MemoryRouter>,
      );

      fireEvent.click(screen.getByRole("button", { name: /Sign In/i }));

      await waitFor(() => {
        expect(screen.getByText(/Username or email is required/i)).toBeInTheDocument();
        expect(screen.getByText(/Password is required/i)).toBeInTheDocument();
      });

      expect(mockLogin).not.toHaveBeenCalled();
    });

    it("submits valid credentials and calls login", async () => {
      mockLogin.mockResolvedValueOnce(undefined);

      render(
        <MemoryRouter>
          <LoginPage />
        </MemoryRouter>,
      );

      fireEvent.change(screen.getByLabelText(/Username or Email/i), {
        target: { value: "grower_user" },
      });
      fireEvent.change(screen.getByLabelText(/Password/i), {
        target: { value: "validPassword123" },
      });

      fireEvent.click(screen.getByRole("button", { name: /Sign In/i }));

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith({
          identifier: "grower_user",
          password: "validPassword123",
        });
      });
    });
  });

  describe("RegisterPage", () => {
    it("renders register form elements correctly", () => {
      render(
        <MemoryRouter>
          <RegisterPage />
        </MemoryRouter>,
      );

      expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /Create Account/i })).toBeInTheDocument();
      expect(screen.getByText(/Already have an account\?/i)).toBeInTheDocument();
    });

    it("validates invalid email format and password length", async () => {
      render(
        <MemoryRouter>
          <RegisterPage />
        </MemoryRouter>,
      );

      fireEvent.change(screen.getByLabelText(/Email Address/i), {
        target: { value: "not-an-email" },
      });
      fireEvent.change(screen.getByLabelText(/Username/i), {
        target: { value: "us" }, // min 3 chars
      });
      fireEvent.change(screen.getByLabelText(/Password/i), {
        target: { value: "short" }, // min 8 chars
      });

      fireEvent.click(screen.getByRole("button", { name: /Create Account/i }));

      await waitFor(() => {
        expect(screen.getByText(/Please enter a valid email address/i)).toBeInTheDocument();
        expect(screen.getByText(/Username must be at least 3 characters/i)).toBeInTheDocument();
        expect(screen.getByText(/Password must be at least 8 characters/i)).toBeInTheDocument();
      });

      expect(mockRegister).not.toHaveBeenCalled();
    });

    it("submits valid registration data and calls register", async () => {
      mockRegister.mockResolvedValueOnce(undefined);

      render(
        <MemoryRouter>
          <RegisterPage />
        </MemoryRouter>,
      );

      fireEvent.change(screen.getByLabelText(/Email Address/i), {
        target: { value: "grower@sunflower.kh" },
      });
      fireEvent.change(screen.getByLabelText(/Username/i), {
        target: { value: "grower_kh" },
      });
      fireEvent.change(screen.getByLabelText(/Password/i), {
        target: { value: "securePassword123!" },
      });

      fireEvent.click(screen.getByRole("button", { name: /Create Account/i }));

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          email: "grower@sunflower.kh",
          username: "grower_kh",
          password: "securePassword123!",
        });
      });
    });
  });
});
