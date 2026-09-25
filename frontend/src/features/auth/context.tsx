import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { setOnRefreshNeeded, setTokenGetter } from "@/api/client";
import { loginApi, logoutApi, refreshApi, registerApi, updateMeApi } from "./api";
import { singleFlightRefresh } from "./refresh";
import type { LoginCredentials, RegisterCredentials, UpdateMeCredentials, User } from "./types";

const USER_STORAGE_KEY = "sunflower_auth_user";
const TOKEN_STORAGE_KEY = "sunflower_access_token";

function getStoredUser(): User | null {
  try {
    const raw = localStorage.getItem(USER_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
}

function getStoredToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
  } catch {
    return null;
  }
}

function saveStoredAuth(token: string | null, userData: User | null): void {
  try {
    if (token && userData) {
      localStorage.setItem(TOKEN_STORAGE_KEY, token);
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData));
    } else {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      localStorage.removeItem(USER_STORAGE_KEY);
    }
  } catch {
    // Ignore storage quota or access errors
  }
}

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  updateProfile: (credentials: UpdateMeCredentials) => Promise<User>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<string | null>;
  hasPermission: (code: string) => boolean;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export interface AuthProviderProps {
  children: ReactNode;
  onSessionExpired?: () => void;
}

export function AuthProvider({ children, onSessionExpired }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(() => getStoredUser());
  const [accessToken, setAccessToken] = useState<string | null>(() => getStoredToken());
  const [isLoading, setIsLoading] = useState<boolean>(() => !getStoredUser());

  // Keep a ref to the latest accessToken so setTokenGetter can read it synchronously
  const tokenRef = useRef<string | null>(accessToken);
  tokenRef.current = accessToken;

  const handleAuthSuccess = useCallback((token: string, userData: User) => {
    tokenRef.current = token;
    setAccessToken(token);
    setUser(userData);
    saveStoredAuth(token, userData);
  }, []);

  const handleAuthClear = useCallback(() => {
    tokenRef.current = null;
    setAccessToken(null);
    setUser(null);
    saveStoredAuth(null, null);
  }, []);

  const refreshSession = useCallback(async (): Promise<string | null> => {
    return singleFlightRefresh(
      async () => {
        const response = await refreshApi();
        handleAuthSuccess(response.access_token, response.user);
        return response.access_token;
      },
      () => {
        handleAuthClear();
        onSessionExpired?.();
      },
    );
  }, [handleAuthSuccess, handleAuthClear, onSessionExpired]);

  // Register token getter and refresh interceptor with API client
  useEffect(() => {
    setTokenGetter(() => tokenRef.current);
    setOnRefreshNeeded(refreshSession);
  }, [refreshSession]);

  // Attempt initial session restoration/validation on mount
  useEffect(() => {
    let mounted = true;

    async function restoreSession() {
      try {
        const response = await refreshApi();
        if (mounted) {
          handleAuthSuccess(response.access_token, response.user);
        }
      } catch {
        if (mounted) {
          // If refresh fails on mount and we have no valid cookie/session, clear stale cache
          handleAuthClear();
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    }

    void restoreSession();

    return () => {
      mounted = false;
    };
  }, [handleAuthSuccess, handleAuthClear]);

  const login = useCallback(
    async (credentials: LoginCredentials): Promise<void> => {
      const response = await loginApi(credentials);
      handleAuthSuccess(response.access_token, response.user);
    },
    [handleAuthSuccess],
  );

  const register = useCallback(
    async (credentials: RegisterCredentials): Promise<void> => {
      const response = await registerApi(credentials);
      handleAuthSuccess(response.access_token, response.user);
    },
    [handleAuthSuccess],
  );

  const updateProfile = useCallback(
    async (credentials: UpdateMeCredentials): Promise<User> => {
      const updatedUser = await updateMeApi(credentials);
      setUser(updatedUser);
      if (tokenRef.current) {
        saveStoredAuth(tokenRef.current, updatedUser);
      }
      return updatedUser;
    },
    [],
  );

  const logout = useCallback(async (): Promise<void> => {
    try {
      await logoutApi();
    } finally {
      handleAuthClear();
    }
  }, [handleAuthClear]);

  const hasPermission = useCallback(
    (code: string): boolean => {
      if (!user || !user.permissions) return false;
      return user.permissions.includes(code);
    },
    [user],
  );

  const value: AuthContextType = {
    user,
    accessToken,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    updateProfile,
    logout,
    refreshSession,
    hasPermission,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export function usePermission(code: string): boolean {
  const { user } = useAuth();
  if (!user || !user.permissions) {
    return false;
  }
  return user.permissions.includes(code);
}

export interface RequirePermissionProps {
  code: string;
  children: ReactNode;
  fallback?: ReactNode;
}

export function RequirePermission({
  code,
  children,
  fallback = null,
}: RequirePermissionProps): React.JSX.Element | null {
  const { isLoading, isAuthenticated } = useAuth();
  const hasPermission = usePermission(code);

  if (isLoading) {
    return null;
  }

  if (!isAuthenticated || !hasPermission) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
