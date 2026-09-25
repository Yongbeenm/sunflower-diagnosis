import type React from "react";
import { useState } from "react";
import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import {
  Plus,
  Pencil,
  Trash2,
  Globe,
  EyeOff,
  Search,
  ChevronLeft,
  ChevronRight,
  Microscope,
  Loader2,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import { useDiseases } from "@/features/diseases/hooks";
import { useUpdateDisease, useDeleteDisease } from "../hooks";
import { useAuth } from "@/features/auth";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ui/ErrorState";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import type { DiseaseListItem } from "@/types/api";

export function DiseasesPage(): React.JSX.Element {
  const { t } = useTranslation();
  const { hasPermission } = useAuth();

  const [search, setSearch] = useState("");
  const [pathogen, setPathogen] = useState("");
  const [publishedFilter, setPublishedFilter] = useState<string>("");
  const [page, setPage] = useState(1);
  const pageSize = 15;

  // Selected disease for deletion confirmation
  const [diseaseToDelete, setDiseaseToDelete] = useState<DiseaseListItem | null>(null);

  const { data, isLoading, isError, refetch } = useDiseases({
    q: search || undefined,
    pathogen: pathogen || undefined,
    published: publishedFilter === "" ? undefined : publishedFilter === "true",
    page,
    size: pageSize,
  });

  const updateMutation = useUpdateDisease();
  const deleteMutation = useDeleteDisease();

  const [feedbackMessage, setFeedbackMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const handleTogglePublish = async (disease: DiseaseListItem) => {
    setFeedbackMessage(null);
    try {
      const nextPublished = !disease.is_published;
      await updateMutation.mutateAsync({
        id: disease.id,
        payload: { is_published: nextPublished },
      });
      setFeedbackMessage({
        type: "success",
        text: nextPublished ? t("admin.publish_success") : t("admin.unpublish_success"),
      });
      setTimeout(() => setFeedbackMessage(null), 4000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : t("admin.publish_error");
      setFeedbackMessage({
        type: "error",
        text: msg,
      });
    }
  };

  const handleConfirmDelete = async () => {
    if (!diseaseToDelete) return;
    try {
      await deleteMutation.mutateAsync(diseaseToDelete.id);
      setDiseaseToDelete(null);
    } catch {
      // Error handled by mutation state
    }
  };

  const totalPages = data ? Math.ceil(data.total / pageSize) : 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Microscope size={22} className="text-amber-500" />
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
              {t("admin.diseases_title")}
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
            {t("admin.diseases_subtitle")}
          </p>
        </div>

        {hasPermission("disease:create") && (
          <Link
            to="/admin/diseases/new"
            className="sf-btn sf-btn--primary sf-btn--sm self-start sm:self-auto flex items-center gap-1.5 font-bold shadow-xs"
          >
            <Plus size={16} />
            <span>{t("admin.new_disease")}</span>
          </Link>
        )}
      </div>

      {feedbackMessage && (
        <div
          className={`sf-alert ${
            feedbackMessage.type === "success" ? "sf-alert--success" : "sf-alert--danger"
          } flex items-center gap-2`}
          role="alert"
        >
          {feedbackMessage.type === "success" ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
          ) : (
            <AlertTriangle className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />
          )}
          <span className="text-xs sm:text-sm font-medium">{feedbackMessage.text}</span>
        </div>
      )}

      {/* Filters Bar */}
      <div className="sf-glass-card p-4 flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            className="w-full pl-9 pr-3.5 py-2 text-xs sm:text-sm rounded-xl bg-white dark:bg-stone-900/70 border border-slate-200 dark:border-slate-700 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all"
            placeholder={t("diseases.search_placeholder")}
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>

        <select
          className="w-full sm:w-auto px-3 py-2 text-xs sm:text-sm rounded-xl bg-white dark:bg-stone-900/70 border border-slate-200 dark:border-slate-700 focus:border-amber-500 outline-none transition-all"
          value={pathogen}
          onChange={(e) => {
            setPathogen(e.target.value);
            setPage(1);
          }}
        >
          <option value="">{t("diseases.all_pathogens")}</option>
          <option value="fungal">{t("diseases.pathogen_fungal")}</option>
          <option value="bacterial">{t("diseases.pathogen_bacterial")}</option>
          <option value="viral">{t("diseases.pathogen_viral")}</option>
          <option value="abiotic">{t("diseases.pathogen_abiotic")}</option>
        </select>

        <select
          className="w-full sm:w-auto px-3 py-2 text-xs sm:text-sm rounded-xl bg-white dark:bg-stone-900/70 border border-slate-200 dark:border-slate-700 focus:border-amber-500 outline-none transition-all"
          value={publishedFilter}
          onChange={(e) => {
            setPublishedFilter(e.target.value);
            setPage(1);
          }}
        >
          <option value="">{t("admin.all_statuses")}</option>
          <option value="true">{t("admin.published_only")}</option>
          <option value="false">{t("admin.draft_only")}</option>
        </select>
      </div>

      {/* Diseases Table */}
      {isLoading ? (
        <div aria-busy="true" className="space-y-2">
          <Skeleton height="3rem" className="rounded-xl" />
          <Skeleton height="15rem" className="rounded-xl" />
        </div>
      ) : isError ? (
        <ErrorState onRetry={() => void refetch()} />
      ) : !data || data.items.length === 0 ? (
        <div className="sf-glass-card p-12 text-center text-slate-500 text-sm">
          {t("diseases.no_results_title")}
        </div>
      ) : (
        <div className="sf-glass-card overflow-hidden border border-slate-200/80 dark:border-slate-800">
          <div className="overflow-x-auto">
            <table className="sf-table">
              <thead>
                <tr>
                  <th>{t("admin.col_name")}</th>
                  <th>{t("admin.col_pathogen")}</th>
                  <th>{t("admin.col_status")}</th>
                  <th style={{ textAlign: "right" }}>{t("admin.col_actions")}</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((disease) => (
                  <tr key={disease.id}>
                    <td>
                      <div className="font-semibold text-slate-900 dark:text-slate-100">
                        {disease.name}
                      </div>
                      <code className="text-[0.7rem] text-slate-400 font-mono">
                        {disease.slug}
                      </code>
                    </td>
                    <td>
                      <Badge variant={disease.pathogen_type}>{disease.pathogen_type}</Badge>
                    </td>
                    <td>
                      <span
                        className={`sf-badge ${
                          disease.is_published ? "sf-badge--success" : "sf-badge--warning"
                        }`}
                        style={{ fontSize: "0.7rem" }}
                      >
                        {disease.is_published ? t("admin.status_published") : t("admin.status_draft")}
                      </span>
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <div className="inline-flex items-center gap-1.5 justify-end">
                        {hasPermission("disease:publish") && (
                          <button
                            type="button"
                            className="sf-btn sf-btn--ghost sf-btn--sm text-xs"
                            disabled={updateMutation.isPending}
                            onClick={() => void handleTogglePublish(disease)}
                            title={disease.is_published ? t("admin.unpublish") : t("admin.publish")}
                          >
                            {updateMutation.isPending ? (
                              <Loader2 size={13} className="animate-spin" />
                            ) : disease.is_published ? (
                              <span className="flex items-center gap-1 text-slate-500">
                                <EyeOff size={13} />
                                <span className="hidden md:inline">{t("admin.unpublish")}</span>
                              </span>
                            ) : (
                              <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400">
                                <Globe size={13} />
                                <span className="hidden md:inline">{t("admin.publish")}</span>
                              </span>
                            )}
                          </button>
                        )}

                        {hasPermission("disease:update") && (
                          <Link
                            to={`/admin/diseases/${disease.slug}`}
                            className="sf-btn sf-btn--secondary sf-btn--sm text-xs flex items-center gap-1"
                          >
                            <Pencil size={13} />
                            <span className="hidden md:inline">{t("admin.edit")}</span>
                          </Link>
                        )}

                        {hasPermission("disease:delete") && (
                          <button
                            type="button"
                            className="sf-btn sf-btn--ghost sf-btn--sm text-xs text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/50"
                            onClick={() => setDiseaseToDelete(disease)}
                            title={t("common.delete")}
                          >
                            <Trash2 size={14} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <nav
          className="flex items-center justify-between pt-2 text-xs"
          aria-label={t("common.pagination")}
        >
          <button
            type="button"
            className="sf-btn sf-btn--secondary sf-btn--sm flex items-center gap-1"
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            <ChevronLeft size={14} />
            <span>{t("common.previous")}</span>
          </button>
          <span className="text-slate-500 font-medium">
            {t("common.page_info", { page, total: totalPages })}
          </span>
          <button
            type="button"
            className="sf-btn sf-btn--secondary sf-btn--sm flex items-center gap-1"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          >
            <span>{t("common.next")}</span>
            <ChevronRight size={14} />
          </button>
        </nav>
      )}

      {/* Deletion Dialog */}
      <ConfirmDialog
        isOpen={diseaseToDelete !== null}
        title={t("admin.confirm_delete_disease_title")}
        message={t("admin.confirm_delete_disease_desc", { name: diseaseToDelete?.name ?? "" })}
        confirmLabel={t("common.delete")}
        isDanger={true}
        isLoading={deleteMutation.isPending}
        onConfirm={() => void handleConfirmDelete()}
        onCancel={() => setDiseaseToDelete(null)}
      />
    </div>
  );
}
