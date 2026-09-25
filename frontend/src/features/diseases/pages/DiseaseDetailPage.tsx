import type React from "react";
import { useMemo } from "react";
import { useParams, Link, useLocation, useNavigate } from "react-router";
import { useTranslation } from "react-i18next";
import {
  ArrowLeft,
  Printer,
  Stethoscope,
  Sparkles,
  ShieldCheck,
  Layers,
  Leaf,
  Info,
  Camera,
} from "lucide-react";
import { useDiseaseDetail } from "../hooks";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ui/ErrorState";

export function DiseaseDetailPage(): React.JSX.Element {
  const { slug } = useParams<{ slug: string }>();
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();

  const { data: disease, isLoading, isError, refetch } = useDiseaseDetail(slug ?? "");

  const matchState = location.state as {
    fromPhotoMatch?: boolean;
    autoCheckSymptomIds?: number[];
    symptomNames?: string[];
    matchedDisease?: {
      disease_id: number;
      slug: string;
      name: string;
      confidence: number;
    };
  } | null;

  const isPhotoMatch = Boolean(matchState?.fromPhotoMatch);

  // Extract all symptom IDs from the disease knowledge model
  const allDiseaseSymptomIds = useMemo(() => {
    if (!disease?.symptom_groups) return [];
    return disease.symptom_groups.flatMap((g) => g.symptoms.map((s) => s.symptom_id));
  }, [disease]);

  const targetSymptomIds = useMemo(() => {
    if (matchState?.autoCheckSymptomIds && matchState.autoCheckSymptomIds.length > 0) {
      return matchState.autoCheckSymptomIds;
    }
    return allDiseaseSymptomIds;
  }, [matchState, allDiseaseSymptomIds]);

  const handleAutoCheckSymptoms = () => {
    if (!disease) return;
    navigate(`/check?disease=${disease.slug}&symptoms=${targetSymptomIds.join(",")}`, {
      state: {
        autoCheckSymptomIds: targetSymptomIds,
        matchedDiseaseName: disease.name,
      },
    });
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6" aria-busy="true">
        <Skeleton height="2rem" width="25%" className="rounded-lg" />
        <Skeleton height="20rem" className="rounded-2xl" />
        <Skeleton height="3rem" width="60%" className="rounded-xl" />
        <Skeleton height="8rem" className="rounded-xl" />
        <Skeleton height="12rem" className="rounded-xl" />
      </div>
    );
  }

  if (isError || !disease) {
    return <ErrorState onRetry={() => void refetch()} />;
  }

  const confidencePercent = matchState?.matchedDisease?.confidence
    ? Math.round(matchState.matchedDisease.confidence * 100)
    : null;
  const isKhmer = i18n.language === "km";

  return (
    <article className="max-w-4xl mx-auto space-y-8">
      {/* Navigation & Action Header */}
      <div className="flex items-center justify-between gap-4">
        <Link
          to="/diseases"
          className="sf-btn sf-btn--ghost sf-btn--sm flex items-center gap-1.5 text-xs font-semibold"
        >
          <ArrowLeft size={14} />
          <span>{t("diseases.back_to_list")}</span>
        </Link>
        <button
          type="button"
          className="sf-btn sf-btn--secondary sf-btn--sm flex items-center gap-1.5 text-xs font-semibold"
          onClick={() => window.print()}
        >
          <Printer size={14} />
          <span>{t("diseases.print")}</span>
        </button>
      </div>

      {/* Photo Match System Notification Banner */}
      {isPhotoMatch && (
        <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-emerald-500/15 via-amber-500/15 to-emerald-500/10 border-2 border-emerald-500/40 shadow-md flex flex-col md:flex-row items-start md:items-center justify-between gap-4 animate-in fade-in slide-in-from-top-3 duration-300">
          <div className="flex items-start gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/25 text-emerald-700 dark:text-emerald-300 flex items-center justify-center shrink-0 shadow-xs">
              <Camera size={20} />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="font-extrabold text-sm sm:text-base text-slate-900 dark:text-slate-100">
                  {isKhmer ? "រូបថតត្រូវគ្នាជាមួយប្រព័ន្ធទិន្នន័យ!" : "Photo Matched in Data System!"}
                </h3>
                {confidencePercent !== null && (
                  <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-600 text-white shadow-xs">
                    {confidencePercent}% {isKhmer ? "ភាពជាក់លាក់" : "match"}
                  </span>
                )}
              </div>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                {isKhmer
                  ? `AI បានវិភាគរូបថតដំណាំរបស់អ្នក ហើយរកឃើញថាត្រូវគ្នានឹងជំងឺ ${disease.name} ក្នុងប្រព័ន្ធ។ រោគសញ្ញាទាំងអស់ត្រូវបានរៀបចំរួចរាល់សម្រាប់អ្នក។`
                  : `Our AI analyzed your uploaded crop photo and matched it to ${disease.name} in the system knowledge base. Matching symptoms are prepared for confirmation.`}
              </p>
              {matchState?.symptomNames && matchState.symptomNames.length > 0 && (
                <div className="pt-1 flex flex-wrap gap-1.5">
                  {matchState.symptomNames.slice(0, 3).map((symName, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded-md text-[0.65rem] font-semibold bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 border border-emerald-300/50 dark:border-emerald-800"
                    >
                      ✓ {symName}
                    </span>
                  ))}
                  {matchState.symptomNames.length > 3 && (
                    <span className="px-1.5 py-0.5 rounded-md text-[0.65rem] font-medium text-slate-500">
                      +{matchState.symptomNames.length - 3} more
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
          <button
            type="button"
            onClick={handleAutoCheckSymptoms}
            className="w-full md:w-auto px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold text-xs sm:text-sm shadow-md flex items-center justify-center gap-2 shrink-0 transition-transform active:scale-95 cursor-pointer"
          >
            <Sparkles size={16} />
            <span>
              {isKhmer
                ? `ធីករោគសញ្ញាស្វ័យប្រវត្តិ (${targetSymptomIds.length})`
                : `Auto-Check Symptoms (${targetSymptomIds.length})`}
            </span>
          </button>
        </div>
      )}

      {/* Hero Visual Card */}
      <div className="sf-glass-card overflow-hidden border border-slate-200/80 dark:border-slate-800">
        <div className="relative w-full aspect-[21/9] sm:aspect-[2/1] bg-slate-100 dark:bg-stone-800/80 overflow-hidden">
          {disease.image_url ? (
            <img
              src={disease.image_url}
              alt={disease.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center text-slate-400 gap-2">
              <span className="text-5xl" aria-hidden="true">
                🌻
              </span>
              <span className="text-xs font-semibold uppercase tracking-wider">
                Clinical Reference Image
              </span>
            </div>
          )}

          {/* Floating pathogen badge */}
          <div className="absolute top-4 right-4 shadow-md">
            <Badge variant={disease.pathogen_type}>{disease.pathogen_type}</Badge>
          </div>
        </div>

        {/* Title Header */}
        <div className="p-6 sm:p-8 space-y-3 bg-white/60 dark:bg-stone-900/70 backdrop-blur-md">
          <div className="space-y-1">
            <div className="text-[0.68rem] font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider font-mono">
              Sunflower Pathology Index • {disease.slug}
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-50">
              {disease.name}
            </h1>
          </div>

          {disease.description && (
            <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed max-w-3xl">
              {disease.description}
            </p>
          )}
        </div>
      </div>

      {/* Main Details Grid */}
      <div className="space-y-6">
        {/* Cause / Etiology */}
        {disease.cause && (
          <section className="sf-glass-card p-6 space-y-3">
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Info size={18} className="text-amber-500" />
              <span>{t("diseases.section_cause")}</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              {disease.cause}
            </p>
          </section>
        )}

        {/* Symptoms Grouped by Plant Part */}
        {disease.symptom_groups && disease.symptom_groups.length > 0 && (
          <section className="sf-glass-card p-6 space-y-4">
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Leaf size={18} className="text-green-600" />
              <span>{t("diseases.section_symptoms")}</span>
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {disease.symptom_groups.map((group) => (
                <div
                  key={group.category.id}
                  className="p-4 rounded-xl bg-slate-50/80 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-700/60 space-y-2.5"
                >
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                    <Layers size={14} className="text-amber-500" />
                    <span>{group.category.label}</span>
                  </h3>

                  <ul className="space-y-2">
                    {group.symptoms.map((sym) => (
                      <li
                        key={sym.symptom_id}
                        className="text-xs text-slate-700 dark:text-slate-200 flex items-start gap-2"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                        <div className="flex-1 min-w-0">
                          <span className="font-medium">{sym.label}</span>
                          <div className="flex items-center gap-1.5 mt-1 flex-wrap">
                            {sym.is_required && (
                              <span className="px-1.5 py-0.5 rounded text-[0.65rem] font-bold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300">
                                {t("diseases.required_symptom")}
                              </span>
                            )}
                            {sym.is_pathognomonic && (
                              <span className="px-1.5 py-0.5 rounded text-[0.65rem] font-bold bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300">
                                {t("diseases.pathognomonic_symptom")}
                              </span>
                            )}
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Treatment & Management */}
        {disease.treatment && (
          <section className="sf-glass-card p-6 space-y-3">
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Stethoscope size={18} className="text-blue-500" />
              <span>{t("diseases.section_treatment")}</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-line">
              {disease.treatment}
            </p>
          </section>
        )}

        {/* Prevention Strategies */}
        {disease.prevention && (
          <section className="sf-glass-card p-6 space-y-3 border-amber-500/20">
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <ShieldCheck size={18} className="text-green-600" />
              <span>{t("diseases.section_prevention")}</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-line">
              {disease.prevention}
            </p>
          </section>
        )}
      </div>

      {/* Clinical Diagnostic CTA Box */}
      <div className="sf-glass-card p-6 sm:p-8 text-center space-y-3 bg-gradient-to-br from-amber-500/10 via-transparent to-green-500/10 border-amber-500/30">
        <div className="w-12 h-12 rounded-2xl bg-amber-500/15 text-amber-600 dark:text-amber-400 flex items-center justify-center mx-auto text-xl shadow-xs">
          <Stethoscope size={24} />
        </div>
        <div className="space-y-1 max-w-md mx-auto">
          <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-slate-100">
            {t("diseases.cta_title")}
          </h3>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
            {t("diseases.cta_desc")}
          </p>
        </div>
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
          <button
            type="button"
            onClick={handleAutoCheckSymptoms}
            className="sf-btn sf-btn--primary sf-btn--md font-bold inline-flex items-center gap-2 cursor-pointer shadow-md"
          >
            <Sparkles size={16} />
            <span>
              {isKhmer
                ? `ធីករោគសញ្ញាស្វ័យប្រវត្តិក្នងប្រព័ន្ធ (${targetSymptomIds.length})`
                : `Auto-Check ${targetSymptomIds.length} Symptoms in Checker`}
            </span>
          </button>
          <Link
            to="/check"
            className="sf-btn sf-btn--secondary sf-btn--md font-bold inline-flex items-center gap-2"
          >
            <Stethoscope size={16} />
            <span>{t("nav.check")}</span>
          </Link>
        </div>
      </div>
    </article>
  );
}
