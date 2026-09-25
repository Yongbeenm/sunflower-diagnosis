import { beforeEach, describe, expect, it, vi } from "vitest";
import { resetSingleFlight, singleFlightRefresh } from "../refresh";

describe("singleFlightRefresh", () => {
  beforeEach(() => {
    resetSingleFlight();
  });

  it("calls refreshFn once when called sequentially", async () => {
    const refreshMock = vi.fn().mockResolvedValue("new-token-123");
    const result = await singleFlightRefresh(refreshMock);

    expect(result).toBe("new-token-123");
    expect(refreshMock).toHaveBeenCalledTimes(1);
  });

  it("deduplicates concurrent refresh calls into a single invocation", async () => {
    let resolveFn: (token: string) => void = () => {};
    const delayedRefresh = vi.fn(
      () =>
        new Promise<string>((resolve) => {
          resolveFn = resolve;
        }),
    );

    // Launch 3 concurrent refreshes
    const promise1 = singleFlightRefresh(delayedRefresh);
    const promise2 = singleFlightRefresh(delayedRefresh);
    const promise3 = singleFlightRefresh(delayedRefresh);

    // Refresh function should only have been called once
    expect(delayedRefresh).toHaveBeenCalledTimes(1);

    // Resolve the single in-flight promise
    resolveFn("shared-token-xyz");

    const [res1, res2, res3] = await Promise.all([promise1, promise2, promise3]);
    expect(res1).toBe("shared-token-xyz");
    expect(res2).toBe("shared-token-xyz");
    expect(res3).toBe("shared-token-xyz");
  });

  it("invokes a new refresh call after the previous one finishes", async () => {
    const refreshMock = vi.fn().mockResolvedValueOnce("token-1").mockResolvedValueOnce("token-2");

    const first = await singleFlightRefresh(refreshMock);
    expect(first).toBe("token-1");

    const second = await singleFlightRefresh(refreshMock);
    expect(second).toBe("token-2");

    expect(refreshMock).toHaveBeenCalledTimes(2);
  });

  it("calls onFailure and returns null if refresh returns empty/null token", async () => {
    const refreshMock = vi.fn().mockResolvedValue(null);
    const failureMock = vi.fn();

    const result = await singleFlightRefresh(refreshMock, failureMock);
    expect(result).toBeNull();
    expect(failureMock).toHaveBeenCalledTimes(1);
  });

  it("calls onFailure and returns null if refreshFn throws an error", async () => {
    const refreshMock = vi.fn().mockRejectedValue(new Error("Network failed"));
    const failureMock = vi.fn();

    const result = await singleFlightRefresh(refreshMock, failureMock);
    expect(result).toBeNull();
    expect(failureMock).toHaveBeenCalledTimes(1);
  });
});
