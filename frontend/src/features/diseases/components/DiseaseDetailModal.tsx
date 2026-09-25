import type React from "react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  X,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ExternalLink,
  Leaf,
} from "lucide-react";
import { PercentageVisualization } from "@/components/ui/PercentageVisualization";
import type { DiagnosisResult, DiseaseDetail } from "@/types/api";

interface DiseaseDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  result?: DiagnosisResult | null | undefined;
  detail?: DiseaseDetail | null | undefined;
  isLoading?: boolean;
}

export function DiseaseDetailModal({
  isOpen,
  onClose,
  result,
  detail,
  isLoading = false,
}: DiseaseDetailModalProps): React.JSX.Element | null {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<
    "overview" | "symptoms" | "analysis" | "recommendations" | "warnings"
  >("overview");

  if (!isOpen) return null;

  const diseaseName = result?.disease.name ?? detail?.name ?? "Disease Assessment";
  const confidence = result?.confidence ?? 0;
  const pathogenType = detail?.pathogen_type ?? "fungal";

  const tabs = [
    { id: "overview", label: t("details.tab_overview") },
    { id: "symptoms", label: t("details.tab_symptoms") },
    { id: "analysis", label: t("details.tab_analysis") },
    { id: "recommendations", label: t("details.tab_recommendations") },
    { id: "warnings", label: t("details.tab_warning_signs") },
  ] as const;

  return (
    <div
      className="sf-modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="disease-modal-title"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="sf-modal-sheet" style={{ maxWidth: "42rem", padding: "1.5rem" }}>
        {/* Header with Title, Match Badge, and Close Button */}
        <div className="flex items-start justify-between gap-4 pb-4 border-b border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center gap-3">
            {detail?.image_url ? (
              <img
                src={detail.image_url}
                alt={diseaseName}
                className="w-14 h-14 rounded-xl object-cover border border-slate-200 dark:border-slate-700 shadow-sm shrink-0"
              />
            ) : (
              <div className="w-14 h-14 rounded-xl bg-amber-500/10 dark:bg-amber-400/10 flex items-center justify-center shrink-0 text-2xl border border-amber-500/20">
                🌻
              </div>
            )}
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="px-2 py-0.5 text-[0.7rem] uppercase font-bold tracking-wider rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                  {pathogenType}
                </span>
                {result && (
                  <span className="px-2 py-0.5 text-[0.7rem] font-bold rounded-md bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300">
                    Rank #{result.rank}
                  </span>
                )}
              </div>
              <h2
                id="disease-modal-title"
                className="text-lg md:text-xl font-bold text-slate-900 dark:text-slate-50 mt-1"
              >
                {diseaseName}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {result && (
              <div className="hidden sm:block">
                <PercentageVisualization value={confidence} size={58} strokeWidth={5} />
              </div>
            )}
            <button
              type="button"
              onClick={onClose}
              className="w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label={t("details.close")}
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex gap-1 overflow-x-auto py-3 border-b border-slate-200/60 dark:border-slate-800 no-scrollbar">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all whitespace-nowrap ${
                activeTab === tab.id
                  ? "bg-amber-500/15 text-amber-900 dark:text-amber-200 border border-amber-500/30"
                  : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="py-4 text-sm text-slate-700 dark:text-slate-300 min-h-[16rem]">
          {isLoading ? (
            <div className="flex items-center justify-center py-12 text-slate-400">
              <span className="sf-spinner" aria-hidden="true" />
            </div>
          ) : (
            <>
              {/* 1. Overview */}
              {activeTab === "overview" && (
                <div className="space-y-4">
                  <div>
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-1">
                      {t("diseases.section_description")}
                    </h3>
                    <p className="leading-relaxed">
                      {detail?.description || t("result.no_match_desc")}
                    </p>
                  </div>

                  {detail?.cause && (
                    <div>
                      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-1">
                        {t("diseases.section_cause")}
                      </h3>
                      <p className="leading-relaxed">{detail.cause}</p>
                    </div>
                  )}

                  {result && (
                    <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-stone-800/60 border border-slate-200/80 dark:border-slate-700/60 flex items-center justify-between gap-4">
                      <div>
                        <div className="text-xs font-bold text-slate-900 dark:text-slate-100">
                          {t("result.match_score")}
                        </div>
                        <div className="text-xs text-slate-500">
                          {confidence >= 0.7
                            ? t("result.confidence_high")
                            : confidence >= 0.4
                              ? t("result.confidence_mid")
                              : t("result.confidence_low")}
                        </div>
                      </div>
                      <div className="w-40">
                        <PercentageVisualization
                          value={confidence}
                          variant="linear"
                          showLabel={true}
                        />
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 2. Symptoms */}
              {activeTab === "symptoms" && (
                <div className="space-y-4">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-2">
                    {t("details.associated_symptoms")}
                  </h3>
                  {detail?.symptom_groups && detail.symptom_groups.length > 0 ? (
                    <div className="space-y-3">
                      {detail.symptom_groups.map((group) => (
                        <div
                          key={group.category.id}
                          className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-700/60"
                        >
                          <div className="text-xs font-bold text-slate-800 dark:text-slate-200 mb-2 flex items-center gap-1.5">
                            <Leaf size={14} className="text-amber-600" />
                            {group.category.label}
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {group.symptoms.map((s) => (
                              <span
                                key={s.symptom_id}
                                className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
                              >
                                <span>{s.label}</span>
                                {s.is_pathognomonic && (
                                  <span className="text-[0.65rem] px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 font-semibold">
                                    {t("details.pathognomonic_badge")}
                                  </span>
                                )}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500">{t("details.no_evidence_available")}</p>
                  )}
                </div>
              )}

              {/* 3. Diagnostic Evidence */}
              {activeTab === "analysis" && (
                <div className="space-y-4">
                  {result?.evidence ? (
                    <div className="space-y-3">
                      {/* Supporting */}
                      {result.evidence.supporting.length > 0 && (
                        <div className="p-3 rounded-xl bg-amber-50/60 dark:bg-amber-950/30 border border-amber-200/60 dark:border-amber-900/40">
                          <div className="text-xs font-bold text-amber-800 dark:text-amber-300 mb-2 flex items-center gap-1.5">
                            <CheckCircle2 size={14} />
                            {t("checker.evidence_supporting")} ({result.evidence.supporting.length})
                          </div>
                          <ul className="space-y-1.5 text-xs">
                            {result.evidence.supporting.map((ev) => (
                              <li
                                key={ev.symptom}
                                className="flex justify-between items-center text-slate-700 dark:text-slate-300"
                              >
                                <span>{ev.symptom}</span>
                                <span className="font-mono text-[0.7rem] px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200">
                                  +{Math.round(ev.weight * 100)}%
                                </span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Against */}
                      {result.evidence.against.length > 0 && (
                        <div className="p-3 rounded-xl bg-rose-50/60 dark:bg-rose-950/30 border border-rose-200/60 dark:border-rose-900/40">
                          <div className="text-xs font-bold text-rose-800 dark:text-rose-300 mb-2 flex items-center gap-1.5">
                            <XCircle size={14} />
                            {t("checker.evidence_against")} ({result.evidence.against.length})
                          </div>
                          <ul className="space-y-1.5 text-xs">
                            {result.evidence.against.map((ev) => (
                              <li
                                key={ev.symptom}
                                className="flex justify-between items-center text-slate-700 dark:text-slate-300"
                              >
                                <span>{ev.symptom}</span>
                                <span className="font-mono text-[0.7rem] px-1.5 py-0.5 rounded bg-rose-100 dark:bg-rose-900 text-rose-800 dark:text-rose-200">
                                  -{Math.round(ev.weight * 100)}%
                                </span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Missing Key */}
                      {result.evidence.missing_key.length > 0 && (
                        <div className="p-3 rounded-xl bg-amber-50/60 dark:bg-amber-950/30 border border-amber-200/60 dark:border-amber-900/40">
                          <div className="text-xs font-bold text-amber-800 dark:text-amber-300 mb-2 flex items-center gap-1.5">
                            <AlertCircle size={14} />
                            {t("checker.evidence_missing")} ({result.evidence.missing_key.length})
                          </div>
                          <ul className="space-y-1.5 text-xs">
                            {result.evidence.missing_key.map((ev) => (
                              <li
                                key={ev.symptom}
                                className="flex justify-between items-center text-slate-700 dark:text-slate-300"
                              >
                                <span>{ev.symptom}</span>
                                <span className="text-[0.7rem] px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200 font-medium">
                                  {t("details.required_badge")}
                                </span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500">{t("details.no_evidence_available")}</p>
                  )}
                </div>
              )}

              {/* 4. Recommendations */}
              {activeTab === "recommendations" && (
                <div className="space-y-4">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-1">
                    {t("diseases.section_treatment")}
                  </h3>
                  <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-700/60 leading-relaxed text-xs sm:text-sm">
                    {detail?.treatment ? (
                      <p className="whitespace-pre-line">{detail.treatment}</p>
                    ) : (
                      <p className="text-slate-400 italic">{t("result.no_match_desc")}</p>
                    )}
                  </div>
                </div>
              )}

              {/* 5. Warning Signs & Prevention */}
              {activeTab === "warnings" && (
                <div className="space-y-4">
                  <div>
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-1">
                      {t("diseases.section_prevention")}
                    </h3>
                    <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-700/60 leading-relaxed text-xs sm:text-sm">
                      {detail?.prevention ? (
                        <p className="whitespace-pre-line">{detail.prevention}</p>
                      ) : (
                        <p className="text-slate-400 italic">
                          Implement crop rotation and clean field sanitation practices.
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-amber-50/70 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/60 flex items-start gap-2.5">
                    <ShieldAlert
                      size={18}
                      className="text-amber-600 dark:text-amber-400 shrink-0 mt-0.5"
                    />
                    <div className="text-xs leading-relaxed text-amber-900 dark:text-amber-200">
                      <strong>When to seek urgent agronomist consultation:</strong> If more than 15%
                      of your field shows rapid stem collapse, wilting, or head rot during humid
                      weather, notify agricultural extension officers immediately.
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Modal Footer with Action Links */}
        <div className="pt-3 border-t border-slate-200/80 dark:border-slate-800 flex items-center justify-between">
          {detail ? (
            <a
              href={`/diseases/${detail.slug}`}
              className="text-xs font-semibold text-amber-700 dark:text-amber-400 hover:underline flex items-center gap-1"
            >
              <span>{t("result.view_guide")}</span>
              <ExternalLink size={13} />
            </a>
          ) : (
            <span />
          )}

          <button type="button" onClick={onClose} className="sf-btn sf-btn--secondary sf-btn--sm">
            {t("details.close")}
          </button>
        </div>
      </div>
    </div>
  );
}
