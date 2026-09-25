/**
 * Typed API client for the Sunflower backend.
 *
 * Usage:
 *   import { apiFetch } from "@/api/client";
 *   const data = await apiFetch<MyType>("/diseases");
 *
 * Token injection:
 *   Call setTokenGetter() with a function that returns the current access
 *   token (or null). AuthProvider does this in Step 3.
 *
 * Refresh interceptor:
 *   setOnRefreshNeeded() registers a callback that is invoked once on a 401
 *   response. Step 3 wires the actual token-rotation logic here.
 */

const rawBase = (import.meta.env["VITE_API_BASE_URL"] as string | undefined)?.trim();
const BASE_URL = (rawBase && rawBase.length > 0 ? rawBase : "/api/v1").replace(/\/+$/, "");

// ---------------------------------------------------------------------------
// Typed error class
// ---------------------------------------------------------------------------

export interface ProblemDetail {
  type?: string;
  title?: string;
  status: number;
  detail?: string;
  errors?: Array<{ field: string; message: string }>;
}

export class ApiError extends Error {
  readonly status: number;
  readonly title: string;
  readonly detail: string;
  readonly errors: Array<{ field: string; message: string }>;

  constructor(problem: ProblemDetail) {
    super(problem.detail ?? problem.title ?? `HTTP ${problem.status}`);
    this.name = "ApiError";
    this.status = problem.status;
    this.title = problem.title ?? "Error";
    this.detail = problem.detail ?? "";
    this.errors = problem.errors ?? [];
  }
}

// ---------------------------------------------------------------------------
// Injectable hooks — wired up in Step 3
// ---------------------------------------------------------------------------

type TokenGetter = () => string | null;
type RefreshCallback = () => Promise<string | null>;

let _tokenGetter: TokenGetter = () => null;
// Step 3: replace this with real refresh logic.
let _onRefreshNeeded: RefreshCallback | null = null;

/** Register a function that returns the current bearer token. */
export function setTokenGetter(fn: TokenGetter): void {
  _tokenGetter = fn;
}

/**
 * Register an async callback that is called once when a 401 is received.
 * It should attempt a token refresh and return the new access token, or null
 * on failure. Step 3 wires this up.
 *
 * @hook Step 3 — token refresh interceptor
 */
export function setOnRefreshNeeded(fn: RefreshCallback): void {
  _onRefreshNeeded = fn;
}

// ---------------------------------------------------------------------------
// Core fetch wrapper
// ---------------------------------------------------------------------------

async function _parseResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type") ?? "";

  if (!response.ok) {
    if (contentType.includes("problem+json") || contentType.includes("application/json")) {
      const problem = (await response.json()) as ProblemDetail;
      throw new ApiError({ ...problem, status: problem.status ?? response.status });
    }
    throw new ApiError({ status: response.status, title: response.statusText });
  }

  if (response.status === 204 || response.headers.get("content-length") === "0") {
    return undefined as unknown as T;
  }

  return (await response.json()) as T;
}

/**
 * Typed fetch wrapper.
 *
 * - Prepends VITE_API_BASE_URL to `path`.
 * - Attaches a bearer token from the registered token getter.
 * - Parses application/problem+json errors into ApiError.
 *
 * On a 401 response the registered refresh callback is invoked once (Step 3).
 * Until Step 3, a 401 surfaces as an ApiError with status 401.
 */
export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = _tokenGetter();

  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (!headers.has("Content-Type") && init.body !== undefined && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (init.body instanceof FormData) {
    headers.delete("Content-Type");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  const url =
    path.startsWith("http://") || path.startsWith("https://") ? path : `${BASE_URL}${cleanPath}`;
  const signal = init.signal ?? AbortSignal.timeout(60000);
  const response = await fetch(url, { ...init, headers, signal, credentials: "include" });

  // --- Refresh interceptor hook (Step 3) ---
  const isAuthPath =
    cleanPath.startsWith("/auth/") ||
    cleanPath === "/auth/refresh" ||
    cleanPath === "/auth/login" ||
    cleanPath === "/auth/register";

  if (response.status === 401 && _onRefreshNeeded && !isAuthPath) {
    // Attempt refresh once, then replay.
    const newToken = await _onRefreshNeeded();
    if (newToken) {
      headers.set("Authorization", `Bearer ${newToken}`);
      const retried = await fetch(url, { ...init, headers, signal, credentials: "include" });
      return _parseResponse<T>(retried);
    }
  }

  return _parseResponse<T>(response);
}
