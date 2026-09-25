import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  activateRuleset,
  createDisease,
  createSymptom,
  deleteDisease,
  deleteSymptom,
  fetchAdminFeedback,
  fetchAdminRoles,
  fetchAdminUsers,
  fetchAnalyticsOverview,
  fetchRulesets,
  updateAdminUser,
  updateDisease,
  updateDiseaseSymptoms,
  updateDiseaseTranslations,
  updateFeedbackStatus,
  updateRolePermissions,
  updateSymptom,
  uploadMedia,
  type CreateDiseasePayload,
  type CreateSymptomPayload,
  type FeedbackStatus,
  type SymptomWeightPayload,
  type UpdateDiseasePayload,
  type UpdateSymptomPayload,
} from "./api";

// ---------------------------------------------------------------------------
// Analytics Hooks
// ---------------------------------------------------------------------------

export function useAnalyticsOverview() {
  return useQuery({
    queryKey: ["admin-analytics-overview"],
    queryFn: fetchAnalyticsOverview,
    staleTime: 30_000,
  });
}

// ---------------------------------------------------------------------------
// Roles & Permissions
// ---------------------------------------------------------------------------

export function useAdminRoles() {
  return useQuery({
    queryKey: ["admin-roles"],
    queryFn: fetchAdminRoles,
  });
}

export function useUpdateRolePermissions() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ roleId, permissionCodes }: { roleId: number; permissionCodes: string[] }) =>
      updateRolePermissions(roleId, permissionCodes),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-roles"] });
    },
  });
}

// ---------------------------------------------------------------------------
// Users
// ---------------------------------------------------------------------------

export function useAdminUsers(page: number = 1, size: number = 20) {
  return useQuery({
    queryKey: ["admin-users", page, size],
    queryFn: () => fetchAdminUsers(page, size),
  });
}

export function useUpdateAdminUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      userId,
      data,
    }: {
      userId: number;
      data: { role_id?: number | undefined; is_active?: boolean | undefined };
    }) => updateAdminUser(userId, data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-users"] });
    },
  });
}

// ---------------------------------------------------------------------------
// Rulesets
// ---------------------------------------------------------------------------

export function useRulesets() {
  return useQuery({
    queryKey: ["admin-rulesets"],
    queryFn: fetchRulesets,
  });
}

export function useActivateRuleset() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (rulesetId: number) => activateRuleset(rulesetId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-rulesets"] });
    },
  });
}

// ---------------------------------------------------------------------------
// Feedback
// ---------------------------------------------------------------------------

export function useAdminFeedback(status?: string, page: number = 1, size: number = 20) {
  return useQuery({
    queryKey: ["admin-feedback", status, page, size],
    queryFn: () => fetchAdminFeedback(status, page, size),
  });
}

export function useUpdateFeedbackStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ feedbackId, status }: { feedbackId: number; status: FeedbackStatus }) =>
      updateFeedbackStatus(feedbackId, status),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-feedback"] });
      void queryClient.invalidateQueries({ queryKey: ["admin-analytics-overview"] });
    },
  });
}

// ---------------------------------------------------------------------------
// Disease Management Hooks
// ---------------------------------------------------------------------------

export function useCreateDisease() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateDiseasePayload) => createDisease(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["diseases"] });
    },
  });
}

export function useUpdateDisease() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: UpdateDiseasePayload }) =>
      updateDisease(id, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["diseases"] });
      void queryClient.invalidateQueries({ queryKey: ["disease-detail"] });
    },
  });
}

export function useDeleteDisease() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteDisease(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["diseases"] });
    },
  });
}

export function useUpdateDiseaseSymptoms() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      diseaseId,
      symptoms,
    }: {
      diseaseId: number;
      symptoms: SymptomWeightPayload[];
    }) => updateDiseaseSymptoms(diseaseId, symptoms),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["disease-detail"] });
    },
  });
}

export function useUpdateDiseaseTranslations() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      diseaseId,
      locale,
      fields,
    }: {
      diseaseId: number;
      locale: string;
      fields: Record<string, string>;
    }) => updateDiseaseTranslations(diseaseId, locale, fields),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["disease-detail"] });
      void queryClient.invalidateQueries({ queryKey: ["diseases"] });
    },
  });
}

// ---------------------------------------------------------------------------
// Symptom Management Hooks
// ---------------------------------------------------------------------------

export function useCreateSymptom() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateSymptomPayload) => createSymptom(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["symptoms-grouped"] });
    },
  });
}

export function useUpdateSymptom() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: UpdateSymptomPayload }) =>
      updateSymptom(id, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["symptoms-grouped"] });
    },
  });
}

export function useDeleteSymptom() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteSymptom(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["symptoms-grouped"] });
    },
  });
}

// ---------------------------------------------------------------------------
// Media Hook
// ---------------------------------------------------------------------------

export function useUploadMedia() {
  return useMutation({
    mutationFn: (file: File) => uploadMedia(file),
  });
}
