import type React from "react";
import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import {
  Stethoscope,
  BookOpen,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Search,
  Cpu,
  FileCheck,
} from "lucide-react";
import { useDiseases } from "@/features/diseases/hooks";
import { DiseaseCard } from "@/features/diseases/components/DiseaseCard";
import { Skeleton } from "@/components/ui/Skeleton";
import { apiFetch } from "@/api/client";

interface SystemStats {
  total_diseases: number;
  total_symptoms: number;
  published_diseases: number;
}

async function fetchSystemStats(): Promise<SystemStats> {
  return apiFetch<SystemStats>("/public/stats");
}

export function LandingPage(): React.JSX.Element {
  const { t } = useTranslation();
  const { data: featuredData, isLoading } = useDiseases({
    page: 1,
    size: 3,
    published: true,
  });

  const { data: stats } = useQuery({
    queryKey: ["system-stats"],
    queryFn: fetchSystemStats,
    staleTime: 60000, // Cache for 1 minute
  });

  return (
    <div className="space-y-12">
      {/* Hero Section with Apple Healthcare + AI Aura */}
      <section className="sf-glass-card p-6 sm:p-12 text-center relative overflow-hidden space-y-6">
        {/* Subtle glowing radial background */}
        <div
          className="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-96 rounded-full bg-amber-400/15 dark:bg-amber-400/10 blur-3xl pointer-events-none"
          aria-hidden="true"
        />

        {/* AI Badge */}
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-100 dark:bg-amber-900/40 border border-amber-300 dark:border-amber-600/50 text-amber-900 dark:text-amber-200 text-xs font-bold uppercase tracking-wider">
          <Sparkles size={13} className="text-amber-700 dark:text-amber-400" />
          <span>Agricultural Expert System</span>
        </div>

        <div className="space-y-3 max-w-2xl mx-auto">
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white leading-tight">
            {t("landing.hero_title")}
          </h1>
          <p className="text-sm sm:text-base text-gray-600 dark:text-gray-300 leading-relaxed font-normal">
            {t("landing.hero_subtitle")}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-center gap-3 flex-wrap pt-2">
          <Link
            to="/check"
            className="sf-btn sf-btn--primary sf-btn--lg text-sm font-bold flex items-center gap-2 shadow-md hover:shadow-lg"
          >
            <Stethoscope size={18} />
            <span>{t("landing.start_checking")}</span>
            <ArrowRight size={16} />
          </Link>

          <Link
            to="/diseases"
            className="sf-btn sf-btn--secondary sf-btn--lg text-sm font-semibold flex items-center gap-2"
          >
            <BookOpen size={18} />
            <span>{t("landing.browse_diseases")}</span>
          </Link>
        </div>

        {/* Live System Metrics */}
        <div className="grid grid-cols-3 max-w-lg mx-auto pt-6 border-t border-gray-200 dark:border-stone-800 gap-3 text-center">
          <div>
            <div className="text-lg sm:text-2xl font-extrabold font-mono text-gray-900 dark:text-white">
              {stats?.published_diseases ?? 5}
            </div>
            <div className="text-[0.68rem] text-gray-600 dark:text-gray-400 uppercase tracking-wider font-bold">
              Diseases & Pathogens
            </div>
          </div>
          <div>
            <div className="text-lg sm:text-2xl font-extrabold font-mono text-gray-900 dark:text-white">
              {stats?.total_symptoms ?? 20}
            </div>
            <div className="text-[0.68rem] text-gray-600 dark:text-gray-400 uppercase tracking-wider font-bold">
              Symptom Indicators
            </div>
          </div>
          <div>
            <div className="text-lg sm:text-2xl font-extrabold font-mono text-amber-800 dark:text-amber-400">
              8 Zones
            </div>
            <div className="text-[0.68rem] text-gray-600 dark:text-gray-400 uppercase tracking-wider font-bold">
              Plant Categories
            </div>
          </div>
        </div>
      </section>

      {/* How It Works 3-Step Interactive Cards */}
      <section className="space-y-6">
        <div className="text-center space-y-1">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
            {t("landing.how_it_works_title")}
          </h2>
          <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300">{t("landing.how_it_works_subtitle")}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="sf-glass-card p-6 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/40 text-amber-900 dark:text-amber-300 flex items-center justify-center font-bold text-base border border-amber-300 dark:border-amber-700/50">
              <Search size={20} />
            </div>
            <h3 className="text-base font-bold text-gray-900 dark:text-white">
              {t("landing.step1_title")}
            </h3>
            <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">{t("landing.step1_desc")}</p>
          </div>

          <div className="sf-glass-card p-6 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/40 text-amber-900 dark:text-amber-300 flex items-center justify-center font-bold text-base border border-amber-300 dark:border-amber-700/50">
              <Cpu size={20} />
            </div>
            <h3 className="text-base font-bold text-gray-900 dark:text-white">
              {t("landing.step2_title")}
            </h3>
            <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">{t("landing.step2_desc")}</p>
          </div>

          <div className="sf-glass-card p-6 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900/40 text-blue-900 dark:text-blue-300 flex items-center justify-center font-bold text-base border border-blue-300 dark:border-blue-700/50">
              <FileCheck size={20} />
            </div>
            <h3 className="text-base font-bold text-gray-900 dark:text-white">
              {t("landing.step3_title")}
            </h3>
            <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">{t("landing.step3_desc")}</p>
          </div>
        </div>
      </section>

      {/* Featured Diseases Reference */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white">
              {t("landing.featured_title")}
            </h2>
            <p className="text-xs text-gray-600 dark:text-gray-300">{t("landing.featured_subtitle")}</p>
          </div>
          <Link
            to="/diseases"
            className="text-xs font-semibold text-amber-900 dark:text-amber-400 hover:underline flex items-center gap-1"
          >
            <span>{t("landing.view_all")}</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4" aria-busy="true">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="sf-glass-card p-4 space-y-3">
                <Skeleton height="9rem" className="rounded-xl" />
                <Skeleton height="1.25rem" width="60%" className="rounded-lg" />
                <Skeleton height="0.875rem" width="90%" className="rounded-md" />
              </div>
            ))}
          </div>
        ) : featuredData && featuredData.items.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {featuredData.items.map((disease) => (
              <DiseaseCard key={disease.id} disease={disease} />
            ))}
          </div>
        ) : null}
      </section>

      {/* Trust & Localization Banner */}
      <section className="sf-glass-card p-6 sm:p-8 text-center space-y-2 border-amber-500/30">
        <div className="flex items-center justify-center gap-2 text-amber-900 dark:text-amber-300 font-bold text-sm">
          <ShieldCheck size={18} />
          <span>{t("landing.trust_title")}</span>
        </div>
        <p className="text-xs text-gray-600 dark:text-gray-300 max-w-xl mx-auto leading-relaxed">
          {t("landing.trust_desc")}
        </p>
      </section>
    </div>
  );
}
