import { apiFetch } from "@/api/client";
import type {
  AdminUserItem,
  AdminUserListResponse,
  AnalyticsOverview,
  FeedbackItem,
  FeedbackListResponse,
  FeedbackStatus,
  MediaResponse,
  RoleItem,
  RoleListResponse,
  RulesetActivateResponse,
  RulesetListResponse,
} from "@/types/api";

export type { FeedbackStatus };

// ---------------------------------------------------------------------------
// Analytics
// ---------------------------------------------------------------------------

export async function fetchAnalyticsOverview(): Promise<AnalyticsOverview> {
  return apiFetch<AnalyticsOverview>("/analytics/overview");
}

// ---------------------------------------------------------------------------
// RBAC Roles & Permissions
// ---------------------------------------------------------------------------

export async function fetchAdminRoles(): Promise<RoleListResponse> {
  return apiFetch<RoleListResponse>("/admin/roles");
}

export async function updateRolePermissions(
  roleId: number,
  permissionCodes: string[],
): Promise<RoleItem> {
  return apiFetch<RoleItem>(`/admin/roles/${String(roleId)}/permissions`, {
    method: "PUT",
    body: JSON.stringify({ permission_codes: permissionCodes }),
  });
}

// ---------------------------------------------------------------------------
// Users
// ---------------------------------------------------------------------------

export async function fetchAdminUsers(
  page: number = 1,
  size: number = 20,
): Promise<AdminUserListResponse> {
  return apiFetch<AdminUserListResponse>(`/admin/users?page=${String(page)}&size=${String(size)}`);
}

export async function updateAdminUser(
  userId: number,
  data: { role_id?: number | undefined; is_active?: boolean | undefined },
): Promise<AdminUserItem> {
  return apiFetch<AdminUserItem>(`/admin/users/${String(userId)}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

// ---------------------------------------------------------------------------
// Rulesets
// ---------------------------------------------------------------------------

export async function fetchRulesets(): Promise<RulesetListResponse> {
  return apiFetch<RulesetListResponse>("/admin/rulesets");
}

export async function activateRuleset(rulesetId: number): Promise<RulesetActivateResponse> {
  return apiFetch<RulesetActivateResponse>(`/admin/rulesets/${String(rulesetId)}/activate`, {
    method: "POST",
  });
}

// ---------------------------------------------------------------------------
// Feedback
// ---------------------------------------------------------------------------

export async function fetchAdminFeedback(
  status?: string,
  page: number = 1,
  size: number = 20,
): Promise<FeedbackListResponse> {
  const params = new URLSearchParams({
    page: String(page),
    size: String(size),
  });
  if (status) params.set("status", status);

  return apiFetch<FeedbackListResponse>(`/feedback?${params.toString()}`);
}

export async function updateFeedbackStatus(
  feedbackId: number,
  status: FeedbackStatus,
): Promise<FeedbackItem> {
  return apiFetch<FeedbackItem>(`/feedback/${String(feedbackId)}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

// ---------------------------------------------------------------------------
// Content Management: Diseases
// ---------------------------------------------------------------------------

export interface CreateDiseasePayload {
  slug: string;
  pathogen_type: string;
  is_published?: boolean | undefined;
  name_en: string;
  description_en?: string | undefined;
  cause_en?: string | undefined;
  treatment_en?: string | undefined;
  prevention_en?: string | undefined;
  name_km?: string | undefined;
  description_km?: string | undefined;
  cause_km?: string | undefined;
  treatment_km?: string | undefined;
  prevention_km?: string | undefined;
  // Legacy fields for backwards compatibility
  name?: string | undefined;
  description?: string | undefined;
  cause?: string | undefined;
  treatment?: string | undefined;
  prevention?: string | undefined;
  translations?: {
    en?: {
      name?: string | undefined;
      description?: string | undefined;
      cause?: string | undefined;
      treatment?: string | undefined;
      prevention?: string | undefined;
    };
    km?: {
      name?: string | undefined;
      description?: string | undefined;
      cause?: string | undefined;
      treatment?: string | undefined;
      prevention?: string | undefined;
    };
  };
}

export async function createDisease(
  payload: CreateDiseasePayload,
): Promise<{ id: number; slug: string }> {
  return apiFetch<{ id: number; slug: string }>("/diseases", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export interface UpdateDiseasePayload {
  slug?: string | undefined;
  pathogen_type?: string | undefined;
  is_published?: boolean | undefined;
  media_id?: number | null | undefined;
  image_media_id?: number | null | undefined;
}

export async function updateDisease(id: number, payload: UpdateDiseasePayload): Promise<void> {
  await apiFetch(`/diseases/${String(id)}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteDisease(id: number): Promise<void> {
  await apiFetch(`/diseases/${String(id)}`, {
    method: "DELETE",
  });
}

export interface SymptomWeightPayload {
  symptom_id: number;
  weight: number;
  is_required: boolean;
  is_pathognomonic: boolean;
}

export async function updateDiseaseSymptoms(
  diseaseId: number,
  symptoms: SymptomWeightPayload[],
): Promise<void> {
  await apiFetch(`/diseases/${String(diseaseId)}/symptoms`, {
    method: "PUT",
    body: JSON.stringify({ symptoms }),
  });
}

export async function updateDiseaseTranslations(
  diseaseId: number,
  locale: string,
  fields: Record<string, string>,
): Promise<void> {
  await apiFetch(`/diseases/${String(diseaseId)}/translations/${encodeURIComponent(locale)}`, {
    method: "PUT",
    body: JSON.stringify(fields),
  });
}

// ---------------------------------------------------------------------------
// Content Management: Symptoms
// ---------------------------------------------------------------------------

export interface CreateSymptomPayload {
  code: string;
  category_id: number;
  label_en: string;
  label_km?: string | undefined;
  is_environmental?: boolean | undefined;
}

export async function createSymptom(
  payload: CreateSymptomPayload,
): Promise<{ id: number; code: string }> {
  return apiFetch<{ id: number; code: string }>("/symptoms", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export interface UpdateSymptomPayload {
  code?: string | undefined;
  category_id?: number | undefined;
  label_en?: string | undefined;
  label_km?: string | undefined;
  is_environmental?: boolean | undefined;
}

export async function updateSymptom(id: number, payload: UpdateSymptomPayload): Promise<void> {
  await apiFetch(`/symptoms/${String(id)}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteSymptom(id: number): Promise<void> {
  await apiFetch(`/symptoms/${String(id)}`, {
    method: "DELETE",
  });
}

// ---------------------------------------------------------------------------
// Media Upload
// ---------------------------------------------------------------------------

export async function uploadMedia(file: File): Promise<MediaResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return apiFetch<MediaResponse>("/media", {
    method: "POST",
    body: formData,
  });
}
