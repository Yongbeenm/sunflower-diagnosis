import { apiFetch } from "@/api/client";
import type {
  Answer,
  CategoryGroupedSymptoms,
  DiagnosisResponse,
  DiagnosisSessionDetail,
  DiagnosisSessionListResponse,
} from "@/types/api";

export async function fetchSymptomsGrouped(locale?: string): Promise<CategoryGroupedSymptoms[]> {
  const searchParams = new URLSearchParams();
  if (locale) searchParams.set("locale", locale);
  const qs = searchParams.toString();
  const path = qs ? `/symptoms?${qs}` : "/symptoms";

  return apiFetch<CategoryGroupedSymptoms[]>(path);
}

export async function previewDiagnosis(
  answers: Record<number, Answer>,
  locale: string,
  signal?: AbortSignal,
): Promise<DiagnosisResponse> {
  const init: RequestInit = {
    method: "POST",
    body: JSON.stringify({ answers, locale }),
  };
  if (signal) {
    init.signal = signal;
  }
  return apiFetch<DiagnosisResponse>("/diagnosis/preview", init);
}

export async function submitDiagnosis(
  answers: Record<number, Answer>,
  locale: string,
): Promise<DiagnosisResponse> {
  return apiFetch<DiagnosisResponse>("/diagnosis/sessions", {
    method: "POST",
    body: JSON.stringify({ answers, locale }),
  });
}

export async function fetchSession(id: string): Promise<DiagnosisSessionDetail> {
  return apiFetch<DiagnosisSessionDetail>(`/diagnosis/sessions/${id}`);
}

export async function fetchSessionHistory(
  page: number = 1,
  size: number = 10,
): Promise<DiagnosisSessionListResponse> {
  return apiFetch<DiagnosisSessionListResponse>(
    `/diagnosis/sessions?page=${String(page)}&size=${String(size)}`,
  );
}
