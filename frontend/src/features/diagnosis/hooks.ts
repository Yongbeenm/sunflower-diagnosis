import { useQuery, useMutation } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import {
  fetchSymptomsGrouped,
  previewDiagnosis,
  submitDiagnosis,
  fetchSession,
  fetchSessionHistory,
} from "./api";
import type { Answer, DiagnosisResponse } from "@/types/api";

export function useSymptomsGrouped() {
  const { i18n } = useTranslation();
  const locale = i18n.language;

  return useQuery({
    queryKey: ["symptoms-grouped", locale],
    queryFn: () => fetchSymptomsGrouped(locale),
    staleTime: 60_000, // symptoms rarely change; cache for 1 min
  });
}

export function useDiagnosisPreview() {
  return useMutation<
    DiagnosisResponse,
    Error,
    { answers: Record<number, Answer>; locale: string; signal?: AbortSignal }
  >({
    mutationFn: ({ answers, locale, signal }) => previewDiagnosis(answers, locale, signal),
  });
}

export function useSubmitDiagnosis() {
  return useMutation<DiagnosisResponse, Error, { answers: Record<number, Answer>; locale: string }>(
    {
      mutationFn: ({ answers, locale }) => submitDiagnosis(answers, locale),
    },
  );
}

export function useSessionDetail(id: string) {
  return useQuery({
    queryKey: ["diagnosis-session", id],
    queryFn: () => fetchSession(id),
    enabled: !!id,
  });
}

export function useSessionHistory(page: number = 1, size: number = 10) {
  return useQuery({
    queryKey: ["diagnosis-history", page, size],
    queryFn: () => fetchSessionHistory(page, size),
  });
}
