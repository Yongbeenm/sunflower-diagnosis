/**
 * Single-flight token refresh manager.
 * Ensures concurrent 401 responses share a single /auth/refresh call
 * rather than initiating a stampede.
 */

let inFlightRefresh: Promise<string | null> | null = null;

export function getInFlightRefresh(): Promise<string | null> | null {
  return inFlightRefresh;
}

export async function singleFlightRefresh(
  refreshFn: () => Promise<string | null>,
  onFailure?: () => void,
): Promise<string | null> {
  if (inFlightRefresh) {
    return inFlightRefresh;
  }

  inFlightRefresh = (async () => {
    try {
      const newToken = await refreshFn();
      if (!newToken) {
        onFailure?.();
        return null;
      }
      return newToken;
    } catch {
      onFailure?.();
      return null;
    } finally {
      inFlightRefresh = null;
    }
  })();

  return inFlightRefresh;
}

/** Reset in-flight state (useful for tests). */
export function resetSingleFlight(): void {
  inFlightRefresh = null;
}
