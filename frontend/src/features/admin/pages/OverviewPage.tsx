import type React from "react";
import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart3,
  Activity,
  Layers,
  HelpCircle,
  MessageSquare,
  ArrowRight,
  TrendingUp,
  Microscope,
  Leaf,
  Database,
  Sparkles,
} from "lucide-react";
import { useAnalyticsOverview } from "../hooks";
import { apiFetch } from "@/api/client";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ui/ErrorState";
import {
  OutbreakTrendChart,
  SymptomDistributionChart,
  ConfidenceDistributionChart,
  DiagnosticHealthGauges,
} from "../components/AdminCharts";

interface SystemStats {
  total_diseases: number;
  total_symptoms: number;
  published_diseases: number;
}

export function OverviewPage(): React.JSX.Element {
  const { t } = useTranslation();
  const { data, isLoading, isError, refetch } = useAnalyticsOverview();

  const { data: stats } = useQuery({
    queryKey: ["system-stats"],
    queryFn: () => apiFetch<SystemStats>("/public/stats"),
    staleTime: 30_000,
  });

  if (isLoading) {
    return (
      <div
        aria-busy="true"
        className="space-y-6 sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl p-6 sm:p-8"
      >
        <Skeleton height="2rem" width="30%" className="rounded-lg" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} height="7rem" className="rounded-xl" />
          ))}
        </div>
        <Skeleton height="18rem" className="rounded-2xl" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton height="16rem" className="rounded-2xl" />
          <Skeleton height="16rem" className="rounded-2xl" />
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl p-6">
        <ErrorState onRetry={() => void refetch()} />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl p-6 sm:p-8">
        <div className="flex items-center gap-2 mb-1">
          <BarChart3 size={24} className="text-amber-500 shrink-0" />
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
            {t("admin.overview_title")}
          </h1>
        </div>
        <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300">
          {t("admin.overview_subtitle")}
        </p>
      </div>

      {/* Knowledge Base Assets & System Totals */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Database size={18} className="text-amber-500" />
            <h2 className="text-sm sm:text-base font-bold text-gray-900 dark:text-white">
              Knowledge Base Inventory & Diagnostics
            </h2>
          </div>
          <span className="text-[0.68rem] font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">
            System Assets
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Diseases Card */}
          <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md p-5 space-y-3 border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl relative overflow-hidden group">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-gray-600 dark:text-gray-300">
                Total Diseases
              </span>
              <div className="w-9 h-9 rounded-xl bg-amber-500/15 text-amber-700 dark:text-amber-400 flex items-center justify-center border border-amber-500/30">
                <Microscope size={19} />
              </div>
            </div>

            <div className="flex items-baseline gap-2">
              <div className="text-3xl sm:text-4xl font-extrabold text-gray-900 dark:text-white font-mono">
                {stats?.total_diseases ?? 5}
              </div>
              <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                {stats?.published_diseases ?? 5} Published
              </span>
            </div>

            <div className="flex items-center justify-between pt-1 border-t border-stone-200/60 dark:border-white/10 text-xs">
              <span className="text-[0.7rem] text-gray-500 dark:text-gray-400 font-medium">
                Fungal, bacterial & viral
              </span>
              <Link
                to="/admin/diseases"
                className="font-bold text-amber-600 dark:text-amber-400 hover:underline flex items-center gap-1"
              >
                <span>Manage</span>
                <ArrowRight size={12} />
              </Link>
            </div>
          </div>

          {/* Symptoms Card */}
          <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md p-5 space-y-3 border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl relative overflow-hidden group">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-gray-600 dark:text-gray-300">
                Total Symptoms
              </span>
              <div className="w-9 h-9 rounded-xl bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 flex items-center justify-center border border-emerald-500/30">
                <Leaf size={19} />
              </div>
            </div>

            <div className="flex items-baseline gap-2">
              <div className="text-3xl sm:text-4xl font-extrabold text-gray-900 dark:text-white font-mono">
                {stats?.total_symptoms ?? 20}
              </div>
              <span className="text-xs font-semibold text-amber-600 dark:text-amber-400">
                8 Plant Zones
              </span>
            </div>

            <div className="flex items-center justify-between pt-1 border-t border-stone-200/60 dark:border-white/10 text-xs">
              <span className="text-[0.7rem] text-gray-500 dark:text-gray-400 font-medium">
                Leaf, stem, head, root, etc.
              </span>
              <Link
                to="/admin/symptoms"
                className="font-bold text-emerald-600 dark:text-emerald-400 hover:underline flex items-center gap-1"
              >
                <span>Manage</span>
                <ArrowRight size={12} />
              </Link>
            </div>
          </div>

          {/* Expert Rulesets & Scoring */}
          <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md p-5 space-y-3 border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl relative overflow-hidden group">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-gray-600 dark:text-gray-300">
                Expert Scoring Rules
              </span>
              <div className="w-9 h-9 rounded-xl bg-blue-500/15 text-blue-700 dark:text-blue-400 flex items-center justify-center border border-blue-500/30">
                <Sparkles size={19} />
              </div>
            </div>

            <div className="flex items-baseline gap-2">
              <div className="text-2xl sm:text-3xl font-extrabold text-gray-900 dark:text-white font-mono">
                16 Rules
              </div>
              <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">
                v2026.09.1
              </span>
            </div>

            <div className="flex items-center justify-between pt-1 border-t border-stone-200/60 dark:border-white/10 text-xs">
              <span className="text-[0.7rem] text-gray-500 dark:text-gray-400 font-medium">
                Weighted Evidence v1
              </span>
              <Link
                to="/admin/symptoms"
                className="font-bold text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
              >
                <span>View Weights</span>
                <ArrowRight size={12} />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Checks Today */}
        <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md p-5 space-y-3 relative overflow-hidden border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-600 dark:text-gray-300">
              {t("admin.stat_checks_today")}
            </span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/15 text-amber-700 dark:text-amber-400 flex items-center justify-center">
              <Activity size={18} />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-gray-900 dark:text-white font-mono">
            {data.checks_today}
          </div>
          <div className="flex items-center gap-1 text-[0.7rem] text-amber-700 dark:text-amber-400 font-semibold">
            <TrendingUp size={12} />
            <span>Active monitoring</span>
          </div>
        </div>

        {/* Checks Total */}
        <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md p-5 space-y-3 relative overflow-hidden border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-600 dark:text-gray-300">
              {t("admin.stat_checks_total")}
            </span>
            <div className="w-8 h-8 rounded-lg bg-blue-500/15 text-blue-700 dark:text-blue-400 flex items-center justify-center">
              <Layers size={18} />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-gray-900 dark:text-white font-mono">
            {data.checks_total}
          </div>
          <div className="text-[0.7rem] text-gray-500 dark:text-gray-400">
            Lifetime session diagnostics
          </div>
        </div>

        {/* Unmatched Patterns */}
        <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md p-5 space-y-3 relative overflow-hidden border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-600 dark:text-gray-300">
              {t("admin.stat_no_match_patterns")}
            </span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/15 text-amber-700 dark:text-amber-400 flex items-center justify-center">
              <HelpCircle size={18} />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-amber-600 dark:text-amber-400 font-mono">
            {data.no_match_patterns.length}
          </div>
          <div className="text-[0.7rem] text-gray-500 dark:text-gray-400">
            Unclassified symptom clusters
          </div>
        </div>

        {/* Pending Feedback */}
        <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md p-5 space-y-3 relative overflow-hidden border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-600 dark:text-gray-300">
              {t("admin.stat_pending_feedback")}
            </span>
            <div className="w-8 h-8 rounded-lg bg-rose-500/15 text-rose-700 dark:text-rose-400 flex items-center justify-center">
              <MessageSquare size={18} />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <div className="text-3xl font-extrabold text-gray-900 dark:text-white font-mono">
              {data.pending_feedback_count}
            </div>
            {data.pending_feedback_count > 0 && (
              <Link
                to="/admin/feedback"
                className="text-xs font-bold text-amber-600 dark:text-amber-400 hover:underline flex items-center gap-1"
              >
                <span>{t("admin.view_queue")}</span>
                <ArrowRight size={12} />
              </Link>
            )}
          </div>
          <div className="text-[0.7rem] text-gray-500 dark:text-gray-400">
            Awaiting agronomist review
          </div>
        </div>
      </div>

      {/* Diagnostic Health & Quality Gauges */}
      <section className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md p-6 border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl">
        <DiagnosticHealthGauges
          checksTotal={data.checks_total}
          noMatchPatterns={data.no_match_patterns}
          pendingFeedback={data.pending_feedback_count}
          topSymptomsCount={data.top_symptoms.length}
        />
      </section>

      {/* Outbreak & 30-Day Activity Area Chart */}
      <section className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md p-6 border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl">
        <OutbreakTrendChart data={data.checks_trend_30d} />
      </section>

      {/* Two Column Section: Top Symptoms Distribution & Diagnostic Confidence Bands */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Symptom Distribution Chart */}
        <section className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md p-6 border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl">
          <SymptomDistributionChart topSymptoms={data.top_symptoms} />
        </section>

        {/* Confidence Rating Distribution */}
        <section className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md p-6 border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl">
          <ConfidenceDistributionChart
            checksTotal={data.checks_total}
            noMatchPatterns={data.no_match_patterns}
          />
        </section>
      </div>

      {/* Unmatched Symptom Patterns for Agronomist Research */}
      <section className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md p-6 space-y-4 border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl">
        <div className="space-y-1">
          <h2 className="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <HelpCircle size={16} className="text-amber-500" />
            <span>{t("admin.no_match_patterns_title")}</span>
          </h2>
          <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
            {t("admin.no_match_patterns_help")}
          </p>
        </div>

        {data.no_match_patterns.length === 0 ? (
          <p className="text-xs text-gray-500 dark:text-gray-400 py-4 text-center">
            {t("admin.no_unmatched_patterns")}
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.no_match_patterns.map((p, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-stone-50/80 dark:bg-[#1E2615]/70 border border-stone-200/70 dark:border-white/10 space-y-2 shadow-xs"
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-amber-600 dark:text-amber-400 font-mono">
                    Pattern #{idx + 1}
                  </span>
                  <span className="text-[0.7rem] text-gray-500 dark:text-gray-400 font-medium">
                    {t("admin.pattern_frequency", { count: p.count })}
                  </span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {p.symptoms.map((sym) => (
                    <span
                      key={sym}
                      className="px-2 py-0.5 rounded-md text-[0.68rem] bg-white dark:bg-[#182010] text-gray-800 dark:text-gray-200 border border-stone-200 dark:border-white/10 font-medium shadow-xs"
                    >
                      {sym}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
