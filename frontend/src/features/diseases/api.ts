import { apiFetch } from "@/api/client";
import type { DiseaseListResponse, DiseaseDetail } from "@/types/api";

export interface FetchDiseasesParams {
  q?: string | undefined;
  category?: string | undefined;
  pathogen?: string | undefined;
  published?: boolean | undefined;
  page?: number | undefined;
  size?: number | undefined;
  locale?: string | undefined;
}

export async function fetchDiseases(
  params: FetchDiseasesParams = {},
): Promise<DiseaseListResponse> {
  const searchParams = new URLSearchParams();

  if (params.q) searchParams.set("q", params.q);
  if (params.category) searchParams.set("category", params.category);
  if (params.pathogen) searchParams.set("pathogen", params.pathogen);
  if (params.published !== undefined) searchParams.set("published", String(params.published));
  if (params.page !== undefined) searchParams.set("page", String(params.page));
  if (params.size !== undefined) searchParams.set("size", String(params.size));
  if (params.locale) searchParams.set("locale", params.locale);

  const qs = searchParams.toString();
  const path = qs ? `/diseases?${qs}` : "/diseases";

  return apiFetch<DiseaseListResponse>(path);
}

export async function fetchDiseaseBySlug(slug: string, locale?: string): Promise<DiseaseDetail> {
  const searchParams = new URLSearchParams();
  if (locale) searchParams.set("locale", locale);

  const qs = searchParams.toString();
  const path = qs ? `/diseases/${slug}?${qs}` : `/diseases/${slug}`;

  return apiFetch<DiseaseDetail>(path);
}
