import { apiFetch } from "@/api/client";
import type { DiagnosisSessionListResponse } from "@/types/api";

/**
 * Fetch the authenticated grower's diagnosis history.
 */
export async function fetchHistory(
  page: number = 1,
  size: number = 10,
): Promise<DiagnosisSessionListResponse> {
  return apiFetch<DiagnosisSessionListResponse>(
    `/diagnosis/sessions?page=${String(page)}&size=${String(size)}`,
  );
}
