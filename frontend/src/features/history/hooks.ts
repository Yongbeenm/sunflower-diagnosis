import { useQuery } from "@tanstack/react-query";
import { fetchHistory } from "./api";

/**
 * Hook to fetch paginated diagnosis history for the authenticated user.
 */
export function useHistory(page: number = 1, size: number = 10) {
  return useQuery({
    queryKey: ["diagnosis-history", page, size],
    queryFn: () => fetchHistory(page, size),
  });
}
