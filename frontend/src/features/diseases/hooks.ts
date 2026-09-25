import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { fetchDiseases, fetchDiseaseBySlug, type FetchDiseasesParams } from "./api";

export function useDiseases(params: FetchDiseasesParams = {}) {
  const { i18n } = useTranslation();
  const locale = params.locale ?? i18n.language;

  return useQuery({
    queryKey: ["diseases", { ...params, locale }],
    queryFn: () => fetchDiseases({ ...params, locale }),
  });
}

export function useDiseaseDetail(slug: string) {
  const { i18n } = useTranslation();
  const locale = i18n.language;

  return useQuery({
    queryKey: ["disease", slug, locale],
    queryFn: () => fetchDiseaseBySlug(slug, locale),
    enabled: !!slug,
  });
}
