import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { apiFetch, ApiError, setTokenGetter, setOnRefreshNeeded } from "../client";

describe("ApiError", () => {
  it("initializes with problem detail fields", () => {
    const error = new ApiError({
      status: 404,
      title: "Not Found",
      detail: "Resource not found",
      type: "/errors/not-found",
      errors: [{ field: "id", message: "Invalid ID" }],
    });

    expect(error.name).toBe("ApiError");
    expect(error.status).toBe(404);
    expect(error.title).toBe("Not Found");
    expect(error.detail).toBe("Resource not found");
    expect(error.message).toBe("Resource not found");
    expect(error.errors).toEqual([{ field: "id", message: "Invalid ID" }]);
  });

  it("falls back to title or default message if detail is missing", () => {
    const error = new ApiError({
      status: 500,
      title: "Server Error",
    });

    expect(error.status).toBe(500);
    expect(error.message).toBe("Server Error");
    expect(error.errors).toEqual([]);
  });
});

describe("apiFetch", () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    setTokenGetter(() => null);
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it("fetches JSON and parses successfully", async () => {
    const mockData = { status: "ok" };
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ "content-type": "application/json" }),
      json: async () => mockData,
    });

    const result = await apiFetch<typeof mockData>("/health");
    expect(result).toEqual(mockData);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/health"),
      expect.objectContaining({
        headers: expect.any(Headers),
      }),
    );
  });

  it("attaches Authorization header when token is present", async () => {
    setTokenGetter(() => "test-token-123");

    globalThis.fetch = vi.fn().mockImplementation((_url, init) => {
      const headers = init?.headers as Headers;
      expect(headers.get("Authorization")).toBe("Bearer test-token-123");
      return Promise.resolve({
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/json" }),
        json: async () => ({}),
      });
    });

    await apiFetch("/test");
  });

  it("throws ApiError with problem+json data on error response", async () => {
    const problem = {
      type: "/errors/validation-failed",
      title: "Validation Failed",
      status: 422,
      detail: "Input failed schema validation",
      errors: [{ field: "name", message: "field required" }],
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 422,
      headers: new Headers({ "content-type": "application/problem+json" }),
      json: async () => problem,
    });

    await expect(apiFetch("/validate")).rejects.toThrow(ApiError);

    try {
      await apiFetch("/validate");
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      const apiErr = err as ApiError;
      expect(apiErr.status).toBe(422);
      expect(apiErr.title).toBe("Validation Failed");
      expect(apiErr.errors).toHaveLength(1);
      expect(apiErr.errors[0]?.field).toBe("name");
    }
  });

  it("allows registering refresh handler via setOnRefreshNeeded", () => {
    const mockCallback = vi.fn().mockResolvedValue(null);
    expect(() => setOnRefreshNeeded(mockCallback)).not.toThrow();
  });
});
