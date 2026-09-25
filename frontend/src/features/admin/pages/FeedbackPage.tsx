import type React from "react";
import { useState } from "react";
import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import {
  MessageSquare,
  Filter,
  Calendar,
  User,
  Stethoscope,
  CheckCircle2,
  Clock,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Inbox,
} from "lucide-react";
import { useAdminFeedback, useUpdateFeedbackStatus } from "../hooks";
import { useAuth } from "@/features/auth";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ui/ErrorState";
import type { FeedbackStatus } from "@/types/api";

const STATUSES: FeedbackStatus[] = ["open", "in_review", "resolved"];

export function FeedbackPage(): React.JSX.Element {
  const { t } = useTranslation();
  const { hasPermission } = useAuth();
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [page, setPage] = useState(1);
  const pageSize = 15;

  const { data, isLoading, isError, refetch } = useAdminFeedback(
    statusFilter || undefined,
    page,
    pageSize,
  );

  const updateStatusMutation = useUpdateFeedbackStatus();

  const handleStatusChange = async (feedbackId: number, status: FeedbackStatus) => {
    await updateStatusMutation.mutateAsync({ feedbackId, status });
  };

  const totalPages = data ? Math.ceil(data.total / pageSize) : 1;

  return (
    <div className="sf-admin-page max-w-7xl mx-auto">
      {/* Header */}
      <div className="sf-admin-page__header flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 dark:bg-amber-400/10 flex items-center justify-center text-amber-600 dark:text-amber-400">
              <MessageSquare className="w-5 h-5" />
            </div>
            <h1 className="sf-admin-page__title text-2xl font-bold tracking-tight">
              {t("admin.feedback_queue_title")}
            </h1>
            {data && (
              <span className="sf-badge sf-badge--neutral text-xs font-semibold px-2.5 py-0.5 rounded-full">
                {data.total} {t("admin.feedback_items", { defaultValue: "reports" })}
              </span>
            )}
          </div>
          <p className="sf-admin-page__desc text-sm text-[var(--color-text-muted)] mt-1">
            {t("admin.feedback_queue_subtitle")}
          </p>
        </div>

        {/* Filter Bar */}
        <div className="flex items-center gap-2">
          <div className="relative inline-flex items-center">
            <Filter className="w-4 h-4 text-[var(--color-text-muted)] absolute left-3 pointer-events-none" />
            <select
              className="sf-form-control text-xs font-medium pl-9 pr-8 py-2 rounded-xl bg-[var(--color-bg-card)] border border-[var(--color-border)] shadow-xs cursor-pointer hover:border-amber-500 transition-colors"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">{t("admin.all_statuses")}</option>
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {t(`admin.feedback_status_${s}`)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div aria-busy="true" className="space-y-4">
          <Skeleton height="3.5rem" className="rounded-2xl" />
          <Skeleton height="18rem" className="rounded-2xl" />
        </div>
      ) : isError ? (
        <ErrorState onRetry={() => void refetch()} />
      ) : !data || data.items.length === 0 ? (
        <div className="sf-card flex flex-col items-center justify-center py-16 text-center border border-dashed border-[var(--color-border)]">
          <div className="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-stone-800/80 flex items-center justify-center text-slate-400 mb-3">
            <Inbox className="w-6 h-6" />
          </div>
          <p className="text-sm font-medium text-[var(--color-text-muted)]">
            {t("admin.no_feedback_reports")}
          </p>
        </div>
      ) : (
        <div className="sf-card p-0 overflow-hidden shadow-sm border border-[var(--color-border)]">
          <div className="overflow-x-auto">
            <table className="sf-table w-full">
              <thead>
                <tr>
                  <th className="font-semibold text-xs uppercase tracking-wider text-[var(--color-text-muted)] py-3.5 px-4">
                    {t("admin.col_subject")}
                  </th>
                  <th className="font-semibold text-xs uppercase tracking-wider text-[var(--color-text-muted)] py-3.5 px-4">
                    {t("admin.col_message")}
                  </th>
                  <th className="font-semibold text-xs uppercase tracking-wider text-[var(--color-text-muted)] py-3.5 px-4">
                    {t("admin.col_session")}
                  </th>
                  <th className="font-semibold text-xs uppercase tracking-wider text-[var(--color-text-muted)] py-3.5 px-4">
                    {t("admin.col_status")}
                  </th>
                  <th className="font-semibold text-xs uppercase tracking-wider text-[var(--color-text-muted)] py-3.5 px-4">
                    {t("admin.col_date")}
                  </th>
                  {hasPermission("feedback:resolve") && (
                    <th className="font-semibold text-xs uppercase tracking-wider text-[var(--color-text-muted)] py-3.5 px-4 text-right">
                      {t("admin.col_actions")}
                    </th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border-subtle)]">
                {data.items.map((item) => (
                  <tr key={item.id} className="transition-colors hover:bg-[var(--color-bg-subtle)]">
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-sm text-[var(--color-text)]">
                        {item.subject}
                      </div>
                      {item.user_name && (
                        <div className="flex items-center gap-1 text-xs text-[var(--color-text-muted)] mt-0.5">
                          <User className="w-3 h-3 opacity-60" />
                          <span>Grower: {item.user_name}</span>
                        </div>
                      )}
                    </td>
                    <td className="py-3.5 px-4 max-w-sm">
                      <p className="text-xs text-[var(--color-text-muted)] line-clamp-2 leading-relaxed">
                        {item.message}
                      </p>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      {item.diagnosis_session_id ? (
                        <Link
                          to={`/check/${item.diagnosis_session_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="sf-btn sf-btn--ghost sf-btn--sm inline-flex items-center gap-1 text-xs font-mono px-2 py-1 rounded bg-slate-100 dark:bg-slate-800 text-amber-600 hover:text-amber-700"
                        >
                          <Stethoscope className="w-3 h-3 text-amber-600" />
                          <span>{item.diagnosis_session_id.slice(0, 8)}…</span>
                        </Link>
                      ) : (
                        <span className="text-xs text-[var(--color-text-muted)]">—</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`sf-badge inline-flex items-center gap-1 text-xs px-2.5 py-0.5 font-medium rounded-full ${
                          item.status === "resolved"
                            ? "sf-badge--success bg-amber-500/10 text-amber-600 dark:text-amber-400"
                            : item.status === "in_review"
                              ? "sf-badge--warning bg-amber-500/10 text-amber-600 dark:text-amber-400"
                              : "sf-badge--error bg-rose-500/10 text-rose-600 dark:text-rose-400"
                        }`}
                      >
                        {item.status === "resolved" ? (
                          <CheckCircle2 className="w-3 h-3" />
                        ) : item.status === "in_review" ? (
                          <Clock className="w-3 h-3" />
                        ) : (
                          <AlertCircle className="w-3 h-3" />
                        )}
                        <span>{t(`admin.feedback_status_${item.status}`)}</span>
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-xs text-[var(--color-text-muted)] whitespace-nowrap">
                      <div className="flex items-center gap-1.5">
                        <Calendar className="w-3.5 h-3.5 opacity-60" />
                        <span>{new Date(item.created_at).toLocaleDateString()}</span>
                      </div>
                    </td>
                    {hasPermission("feedback:resolve") && (
                      <td className="py-3.5 px-4 text-right whitespace-nowrap">
                        <select
                          className="sf-form-control text-xs font-medium px-2.5 py-1 rounded-lg bg-[var(--color-bg)] border-[var(--color-border)] cursor-pointer hover:border-amber-500 transition-colors"
                          value={item.status}
                          disabled={updateStatusMutation.isPending}
                          onChange={(e) =>
                            void handleStatusChange(item.id, e.target.value as FeedbackStatus)
                          }
                        >
                          <option value="open">{t("admin.feedback_status_open")}</option>
                          <option value="in_review">{t("admin.feedback_status_in_review")}</option>
                          <option value="resolved">{t("admin.feedback_status_resolved")}</option>
                        </select>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex flex-col sm:flex-row justify-between items-center gap-3 p-4 border-t border-[var(--color-border)] bg-[var(--color-bg-subtle)]">
              <span className="text-xs text-[var(--color-text-muted)]">
                {t("common.page_info", { page, total: totalPages })}
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  className="sf-btn sf-btn--outline sf-btn--sm inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  <span>{t("common.previous")}</span>
                </button>
                <button
                  type="button"
                  className="sf-btn sf-btn--outline sf-btn--sm inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                >
                  <span>{t("common.next")}</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

