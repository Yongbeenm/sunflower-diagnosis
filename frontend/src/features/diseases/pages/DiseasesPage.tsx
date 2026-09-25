import type React from "react";
import { useState, useEffect } from "react";
import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import { Search, BookOpen, X, ChevronLeft, ChevronRight, Layers } from "lucide-react";
import { useDiseases } from "../hooks";
import { DiseaseCard } from "../components/DiseaseCard";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import type { PathogenType } from "@/types/api";

const PATHOGENS: PathogenType[] = ["fungal", "bacterial", "viral", "abiotic"];

export function DiseasesPage(): React.JSX.Element {
  const { t } = useTranslation();
  const [searchInput, setSearchInput] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [selectedPathogen, setSelectedPathogen] = useState<string>("");
  const [page, setPage] = useState(1);
  const pageSize = 9;

  // Debounce search input by 300ms
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchInput.trim());
      setPage(1); // reset to page 1 on query change
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput]);

  const { data, isLoading, isError, refetch } = useDiseases({
    q: debouncedQuery || undefined,
    pathogen: selectedPathogen || undefined,
    page,
    size: pageSize,
    published: true,
  });

  const totalPages = data ? Math.ceil(data.total / pageSize) : 1;

  const handleSelectPathogen = (pathogen: string) => {
    setSelectedPathogen(selectedPathogen === pathogen ? "" : pathogen);
    setPage(1);
  };

  return (
    <div className="space-y-6">
      {/* Header & Search Bar Banner */}
      <div className="sf-glass-card p-5 sm:p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <BookOpen size={24} className="text-amber-500" />
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
                {t("diseases.title")}
              </h1>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
              {t("diseases.subtitle")}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 self-start sm:self-auto">
            <Link
              to="/diseases/compare"
              className="sf-btn sf-btn--primary sf-btn--sm flex items-center gap-1.5 font-semibold shadow-xs"
            >
              <Layers size={15} />
              <span>{t("compare.btn_compare_from_list")}</span>
            </Link>

            {data && (
              <div className="px-3 py-1 rounded-full bg-slate-100 dark:bg-stone-800 text-xs font-semibold text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-white/10">
                {t("diseases.total_count", { count: data.total, defaultValue: `${data.total} Diseases` })}
              </div>
            )}
          </div>
        </div>

        {/* Search Input */}
        <div className="relative">
          <Search
            size={18}
            className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"
            aria-hidden="true"
          />
          <input
            type="search"
            className="w-full pl-10 pr-10 py-2.5 text-sm rounded-xl bg-white dark:bg-stone-900/70 border border-slate-200 dark:border-slate-700/80 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all"
            placeholder={t("diseases.search_placeholder")}
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            aria-label={t("diseases.search_placeholder")}
          />
          {searchInput && (
            <button
              type="button"
              onClick={() => setSearchInput("")}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              aria-label="Clear search"
            >
              <X size={16} />
            </button>
          )}
        </div>

        {/* Pathogen Filter Pills */}
        <div className="flex items-center gap-1.5 flex-wrap pt-1">
          <button
            type="button"
            onClick={() => handleSelectPathogen("")}
            className={`sf-chip text-xs ${
              selectedPathogen === ""
                ? "bg-slate-900 text-white dark:bg-white dark:text-slate-900 border-transparent shadow-xs"
                : ""
            }`}
          >
            <span>{t("diseases.all_pathogens")}</span>
          </button>

          {PATHOGENS.map((p) => {
            const isSelected = selectedPathogen === p;
            return (
              <button
                key={p}
                type="button"
                onClick={() => handleSelectPathogen(p)}
                className={`sf-chip text-xs ${
                  isSelected
                    ? "bg-amber-500 text-slate-950 font-bold border-amber-600 shadow-xs"
                    : ""
                }`}
              >
                <span>{t(`diseases.pathogen_${p}`)}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Content states */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4" aria-busy="true">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="sf-glass-card p-4 space-y-3">
              <Skeleton height="10rem" className="rounded-xl" />
              <Skeleton height="1.25rem" width="65%" className="rounded-lg" />
              <Skeleton height="0.875rem" width="90%" className="rounded-md" />
              <Skeleton height="0.875rem" width="70%" className="rounded-md" />
            </div>
          ))}
        </div>
      ) : isError ? (
        <ErrorState onRetry={() => void refetch()} />
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={<Search size={28} />}
          title={t("diseases.no_results_title")}
          description={t("diseases.no_results_desc")}
          action={
            searchInput || selectedPathogen ? (
              <button
                type="button"
                className="sf-btn sf-btn--secondary sf-btn--sm"
                onClick={() => {
                  setSearchInput("");
                  setSelectedPathogen("");
                  setPage(1);
                }}
              >
                {t("diseases.clear_filters")}
              </button>
            ) : undefined
          }
        />
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.items.map((disease) => (
              <DiseaseCard key={disease.id} disease={disease} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <nav
              className="flex items-center justify-between pt-4 border-t border-slate-200/60 dark:border-slate-800 text-xs"
              aria-label={t("common.pagination")}
            >
              <button
                type="button"
                className="sf-btn sf-btn--secondary sf-btn--sm flex items-center gap-1"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                aria-label={t("common.previous")}
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
                aria-label={t("common.next")}
              >
                <span>{t("common.next")}</span>
                <ChevronRight size={14} />
              </button>
            </nav>
          )}
        </div>
      )}
    </div>
  );
}
