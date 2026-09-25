import type React from "react";
import { useState } from "react";
import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import { Clock, ChevronRight, Stethoscope, LogIn, Calendar } from "lucide-react";
import { useAuth } from "@/features/auth";
import { useHistory } from "../hooks";
import { PercentageVisualization } from "@/components/ui/PercentageVisualization";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ui/ErrorState";

export function HistoryPage(): React.JSX.Element {
  const { t } = useTranslation();
  const { isAuthenticated, isLoading: isAuthLoading, user } = useAuth();
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const { data, isLoading, isError, refetch } = useHistory(page, pageSize);

  if (isAuthLoading && !user) {
    return (
      <div className="max-w-3xl mx-auto space-y-6 sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl p-6 sm:p-8" aria-busy="true">
        <Skeleton height="2.5rem" width="30%" className="mb-2" />
        <Skeleton height="1.25rem" width="50%" className="mb-6" />
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} height="5rem" className="rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (!isAuthenticated && !user) {
    return (
      <div className="max-w-md mx-auto my-12 text-center sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl p-8 space-y-4">
        <div className="w-14 h-14 rounded-2xl bg-amber-500/15 text-amber-800 dark:text-amber-400 flex items-center justify-center mx-auto text-2xl border border-amber-500/30">
          🔒
        </div>
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">
          {t("history.auth_required_title")}
        </h2>
        <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
          {t("history.auth_required_desc")}
        </p>
        <Link
          to="/login"
          state={{ from: "/history" }}
          className="sf-btn sf-btn--primary sf-btn--md inline-flex items-center gap-1.5"
        >
          <LogIn size={16} />
          <span>{t("nav.login")}</span>
        </Link>
      </div>
    );
  }

  const totalPages = data ? Math.ceil(data.total / pageSize) : 1;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header Glass Card */}
      <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl p-6 sm:p-8">
        <div className="flex items-center gap-2 mb-1">
          <Clock size={24} className="text-amber-600 dark:text-amber-400 shrink-0" />
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
            {t("history.title")}
          </h1>
        </div>
        <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300">
          {t("history.subtitle")}
        </p>
      </div>

      {isLoading ? (
        <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl p-6 space-y-3" aria-busy="true">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} height="5rem" className="rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl p-6">
          <ErrorState onRetry={() => void refetch()} />
        </div>
      ) : !data || data.items.length === 0 ? (
        <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl p-10 text-center space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-amber-500/10 dark:bg-amber-400/10 text-amber-700 dark:text-amber-400 flex items-center justify-center mx-auto text-2xl border border-amber-500/20">
            📋
          </div>
          <h2 className="text-base font-bold text-gray-900 dark:text-white">
            {t("history.empty_title")}
          </h2>
          <p className="text-xs text-gray-600 dark:text-gray-400 max-w-sm mx-auto leading-relaxed">
            {t("history.empty_desc")}
          </p>
          <Link to="/check" className="sf-btn sf-btn--primary inline-flex items-center gap-1.5">
            <Stethoscope size={16} />
            <span>{t("nav.check")}</span>
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="space-y-3">
            {data.items.map((session) => {
              const formattedDate = new Date(session.created_at).toLocaleDateString(undefined, {
                year: "numeric",
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              });

              return (
                <Link
                  key={session.id}
                  to={`/check/${session.id}`}
                  className="sf-glass-card bg-white/90 dark:bg-[#222C19]/85 backdrop-blur-md border border-stone-200/90 dark:border-white/10 shadow-sm hover:shadow-md hover:border-amber-500/60 p-4 sm:p-5 flex items-center justify-between gap-3 transition-all hover:translate-y-[-2px] group block rounded-xl"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-bold text-sm text-gray-900 dark:text-white group-hover:text-amber-700 dark:group-hover:text-amber-400 transition-colors">
                        {session.top_disease
                          ? session.top_disease.name
                          : t("history.no_disease_match")}
                      </span>
                      {session.outcome === "no_match" && (
                        <span className="px-2 py-0.5 text-[0.65rem] font-bold rounded-full bg-amber-500/15 text-amber-900 dark:text-amber-300 border border-amber-500/30">
                          {t("history.no_match")}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-300 font-medium">
                      <Calendar size={13} className="shrink-0" />
                      <span>{formattedDate}</span>
                      <span>•</span>
                      <span>{t("history.symptoms_count", { count: session.symptom_count })}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    {session.top_confidence !== null && session.top_confidence > 0 && (
                      <div className="w-24 hidden sm:block">
                        <PercentageVisualization
                          value={session.top_confidence}
                          variant="linear"
                          showLabel={true}
                        />
                      </div>
                    )}
                    <ChevronRight
                      size={18}
                      className="text-gray-400 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-transform group-hover:translate-x-0.5"
                    />
                  </div>
                </Link>
              );
            })}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-md rounded-xl p-4 flex items-center justify-between text-xs">
              <button
                type="button"
                className="sf-btn sf-btn--secondary sf-btn--sm font-bold"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                ← {t("common.previous")}
              </button>

              <span className="text-gray-600 dark:text-gray-300 font-semibold">
                {t("common.page_info", { page, total: totalPages })}
              </span>

              <button
                type="button"
                className="sf-btn sf-btn--secondary sf-btn--sm font-bold"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              >
                {t("common.next")} →
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
