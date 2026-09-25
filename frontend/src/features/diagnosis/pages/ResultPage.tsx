import type React from "react";
import { useState } from "react";
import { useParams, Link, useLocation } from "react-router";
import { useTranslation } from "react-i18next";
import {
  Printer,
  RotateCcw,
  MessageSquare,
  ShieldAlert,
  Sparkles,
  ExternalLink,
  ChevronRight,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Download,
  Share2,
} from "lucide-react";
import { useSessionDetail } from "../hooks";
import { useDiseaseDetail } from "@/features/diseases/hooks";
import { PercentageVisualization } from "@/components/ui/PercentageVisualization";
import { DiseaseDetailModal } from "@/features/diseases/components/DiseaseDetailModal";
import { DiagnosticReportModal } from "../components/DiagnosticReportModal";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ui/ErrorState";
import type { DiagnosisResponse, DiagnosisResult } from "@/types/api";

export function ResultPage(): React.JSX.Element {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { t } = useTranslation();
  const location = useLocation();

  const [selectedResult, setSelectedResult] = useState<DiagnosisResult | null>(null);
  const [isReportModalOpen, setIsReportModalOpen] = useState<boolean>(false);

  const directResult = (location.state as { result?: DiagnosisResponse } | null)?.result;

  const {
    data: session,
    isLoading,
    isError,
    refetch,
  } = useSessionDetail(sessionId && sessionId !== "result" ? sessionId : "");

  // Load detail when a candidate is inspected
  const { data: inspectedDetail, isLoading: isInspecting } = useDiseaseDetail(
    selectedResult?.disease.slug ?? "",
  );

  const displayData =
    session ??
    (directResult
      ? {
          session_id: directResult.session_id ?? "preview",
          ruleset_version: directResult.ruleset_version,
          outcome: directResult.outcome,
          locale: "en",
          created_at: new Date().toISOString(),
          symptom_count: 0,
          selected_symptoms: [],
          results: directResult.results,
          next_best_questions: directResult.next_best_questions,
          feedback_prompt: directResult.feedback_prompt,
        }
      : null);

  if (isLoading) {
    return (
      <div aria-busy="true" className="max-w-4xl mx-auto space-y-6">
        <Skeleton height="2.5rem" width="45%" className="rounded-xl" />
        <Skeleton height="1.25rem" width="70%" className="rounded-lg" />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} height="5rem" className="rounded-xl" />
          ))}
        </div>
        <Skeleton height="14rem" className="rounded-2xl" />
        <Skeleton height="14rem" className="rounded-2xl" />
      </div>
    );
  }

  if (isError || !displayData) {
    return <ErrorState onRetry={() => void refetch()} />;
  }

  const isMatched = displayData.outcome === "matched" && displayData.results.length > 0;
  const topResult = isMatched ? displayData.results[0] : null;
  const evaluatedSymptomsCount = (session?.symptom_count ?? displayData.results.length > 0) ? 8 : 0;
  const totalAnalyzedDiseases = 26; // Complete database disease catalog count

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Disease Detail Inspection Modal */}
      <DiseaseDetailModal
        isOpen={selectedResult !== null}
        onClose={() => setSelectedResult(null)}
        result={selectedResult}
        detail={inspectedDetail}
        isLoading={isInspecting}
      />

      {/* Full Diagnostic PDF Report Preview & Export Modal */}
      <DiagnosticReportModal
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
        session={session ?? null}
        results={displayData.results}
      />

      {/* Top Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl" aria-hidden="true">
              📊
            </span>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
              {t("result.title")}
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
            {t("result.subtitle")}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 self-start sm:self-auto">
          {/* Export PDF Button */}
          {isMatched && (
            <button
              type="button"
              onClick={() => setIsReportModalOpen(true)}
              className="sf-btn sf-btn--primary sf-btn--sm flex items-center gap-1.5 cursor-pointer font-semibold"
              title={t("report.btn_download_pdf")}
            >
              <Download size={15} />
              <span>{t("report.btn_download_pdf")}</span>
            </button>
          )}

          {/* Share Report Button */}
          {isMatched && (
            <button
              type="button"
              onClick={() => setIsReportModalOpen(true)}
              className="sf-btn sf-btn--secondary sf-btn--sm flex items-center gap-1.5 cursor-pointer font-semibold"
              title={t("report.btn_share")}
            >
              <Share2 size={15} />
              <span>{t("report.btn_share")}</span>
            </button>
          )}

          <button
            type="button"
            onClick={() => window.print()}
            className="sf-btn sf-btn--secondary sf-btn--sm flex items-center gap-1.5"
          >
            <Printer size={15} />
            <span>{t("diseases.print")}</span>
          </button>

          <Link to="/check" className="sf-btn sf-btn--secondary sf-btn--sm flex items-center gap-1.5">
            <RotateCcw size={15} />
            <span>{t("result.start_new")}</span>
          </Link>
        </div>
      </div>

      {/* Analysis Summary Statistics Dashboard */}
      {isMatched && topResult && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="sf-glass-card p-3.5 space-y-1">
            <div className="text-[0.7rem] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              {t("result.stat_symptoms")}
            </div>
            <div className="text-xl font-bold text-slate-900 dark:text-slate-100">
              {session?.selected_symptoms.length ?? evaluatedSymptomsCount}
            </div>
          </div>

          <div className="sf-glass-card p-3.5 space-y-1">
            <div className="text-[0.7rem] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              {t("result.stat_analyzed")}
            </div>
            <div className="text-xl font-bold text-slate-900 dark:text-slate-100">
              {totalAnalyzedDiseases}
            </div>
          </div>

          <div className="sf-glass-card p-3.5 space-y-1">
            <div className="text-[0.7rem] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 truncate">
              {t("result.stat_top_match")}
            </div>
            <div className="text-base font-bold text-slate-900 dark:text-slate-100 truncate">
              {topResult.disease.name}
            </div>
          </div>

          <div className="sf-glass-card p-3.5 space-y-1 border-amber-500/30">
            <div className="text-[0.7rem] font-bold uppercase tracking-wider text-amber-800 dark:text-amber-300">
              {t("result.stat_confidence")}
            </div>
            <div className="text-xl font-bold text-amber-700 dark:text-amber-400 flex items-center gap-1">
              <PercentageVisualization
                value={topResult.confidence}
                variant="number"
                className="font-mono text-xl"
              />
            </div>
          </div>
        </div>
      )}

      {/* Medical Safety Disclaimer UX */}
      <div className="p-3.5 sm:p-4 rounded-2xl bg-amber-500/10 dark:bg-amber-400/10 border border-amber-500/25 flex items-start gap-3">
        <ShieldAlert
          size={20}
          className="text-amber-600 dark:text-amber-400 shrink-0 mt-0.5"
          aria-hidden="true"
        />
        <div className="space-y-0.5">
          <div className="text-xs font-bold text-amber-900 dark:text-amber-200">
            Agricultural Decision-Support Disclaimer
          </div>
          <p className="text-xs text-amber-800/90 dark:text-amber-300/90 leading-relaxed">
            {t("result.medical_disclaimer")}
          </p>
        </div>
      </div>

      {/* Ranked Candidate Cards */}
      {isMatched ? (
        <div className="space-y-4">
          {displayData.results.map((result, index) => {
            const isTop = index === 0;

            return (
              <div
                key={result.disease.slug}
                className={`sf-glass-card sf-stagger-item p-4 sm:p-6 space-y-4 transition-all ${
                  isTop
                    ? "border-amber-500/40 shadow-lg ring-1 ring-amber-500/20"
                    : "hover:border-slate-300 dark:hover:border-slate-700"
                }`}
                style={{ animationDelay: `${index * 80}ms` }}
              >
                {/* Header: Title, Badges, and Gauge */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-slate-200/60 dark:border-slate-800">
                  <div className="flex items-start gap-3">
                    <span
                      className={`px-2 py-1 text-xs font-bold rounded-lg shrink-0 ${
                        isTop
                          ? "bg-amber-500 text-slate-950 shadow-sm"
                          : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300"
                      }`}
                    >
                      #{result.rank}
                    </span>

                    <div>
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        {isTop && (
                          <span className="px-2 py-0.5 text-[0.65rem] font-bold rounded-md bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 uppercase tracking-wider flex items-center gap-1">
                            <Sparkles size={10} />
                            <span>{t("result.top_match_badge")}</span>
                          </span>
                        )}
                        <span className="text-xs text-slate-400">
                          {result.confidence >= 0.7
                            ? t("result.confidence_high")
                            : result.confidence >= 0.4
                              ? t("result.confidence_mid")
                              : t("result.confidence_low")}
                        </span>
                      </div>

                      <h2 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-slate-50">
                        {result.disease.name}
                      </h2>
                    </div>
                  </div>

                  {/* Circular Percentage Visualization Gauge */}
                  <div className="flex items-center gap-4 self-end sm:self-center">
                    <PercentageVisualization
                      value={result.confidence}
                      size={isTop ? 88 : 74}
                      strokeWidth={isTop ? 8 : 7}
                      sublabel={t("result.match_score")}
                    />
                  </div>
                </div>

                {/* Evidence Breakdown Pills */}
                <div className="space-y-3">
                  <div className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                    Contributing Observed Evidence
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
                    {/* Supporting Symptoms */}
                    <div className="p-3 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/50 dark:border-amber-900/30">
                      <div className="text-xs font-bold text-amber-800 dark:text-amber-300 mb-1.5 flex items-center gap-1">
                        <CheckCircle2 size={13} />
                        <span>{t("checker.evidence_supporting")}</span>
                        <span className="text-[0.65rem] text-amber-600 dark:text-amber-400">
                          ({result.evidence.supporting.length})
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {result.evidence.supporting.length > 0 ? (
                          result.evidence.supporting.map((ev) => (
                            <span
                              key={ev.symptom}
                              className="inline-flex items-center gap-1 px-2 py-0.5 text-[0.7rem] font-medium rounded-md bg-white dark:bg-slate-900 border border-amber-200 dark:border-amber-900/60 text-slate-800 dark:text-slate-200"
                            >
                              <span>{ev.symptom}</span>
                              <span className="text-amber-700 dark:text-amber-400 font-mono text-[0.65rem]">
                                +{Math.round(ev.weight * 100)}%
                              </span>
                            </span>
                          ))
                        ) : (
                          <span className="text-[0.7rem] text-slate-400 italic">None observed</span>
                        )}
                      </div>
                    </div>

                    {/* Conflicting Symptoms */}
                    <div className="p-3 rounded-xl bg-rose-50/50 dark:bg-rose-950/20 border border-rose-200/50 dark:border-rose-900/30">
                      <div className="text-xs font-bold text-rose-800 dark:text-rose-300 mb-1.5 flex items-center gap-1">
                        <XCircle size={13} />
                        <span>{t("checker.evidence_against")}</span>
                        <span className="text-[0.65rem] text-rose-600 dark:text-rose-400">
                          ({result.evidence.against.length})
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {result.evidence.against.length > 0 ? (
                          result.evidence.against.map((ev) => (
                            <span
                              key={ev.symptom}
                              className="inline-flex items-center gap-1 px-2 py-0.5 text-[0.7rem] font-medium rounded-md bg-white dark:bg-slate-900 border border-rose-200 dark:border-rose-900/60 text-slate-800 dark:text-slate-200"
                            >
                              <span>{ev.symptom}</span>
                              <span className="text-rose-700 dark:text-rose-400 font-mono text-[0.65rem]">
                                -{Math.round(ev.weight * 100)}%
                              </span>
                            </span>
                          ))
                        ) : (
                          <span className="text-[0.7rem] text-slate-400 italic">
                            No conflicting indicators
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Missing Key Indicators */}
                    <div className="p-3 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/50 dark:border-amber-900/30">
                      <div className="text-xs font-bold text-amber-800 dark:text-amber-300 mb-1.5 flex items-center gap-1">
                        <AlertTriangle size={13} />
                        <span>{t("checker.evidence_missing")}</span>
                        <span className="text-[0.65rem] text-amber-600 dark:text-amber-400">
                          ({result.evidence.missing_key.length})
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {result.evidence.missing_key.length > 0 ? (
                          result.evidence.missing_key.map((ev) => (
                            <span
                              key={ev.symptom}
                              className="inline-flex items-center px-2 py-0.5 text-[0.7rem] font-medium rounded-md bg-white dark:bg-slate-900 border border-amber-200 dark:border-amber-900/60 text-slate-800 dark:text-slate-200"
                            >
                              {ev.symptom}
                            </span>
                          ))
                        ) : (
                          <span className="text-[0.7rem] text-slate-400 italic">
                            All key indicators present
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Card Actions: View Details Modal + Full Guide Link */}
                <div className="pt-2 flex items-center justify-between flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => setSelectedResult(result)}
                    className="sf-btn sf-btn--secondary sf-btn--sm flex items-center gap-1.5"
                  >
                    <span>{t("result.view_details_btn")}</span>
                    <ChevronRight size={14} />
                  </button>

                  <Link
                    to={`/diseases/${result.disease.slug}`}
                    className="text-xs font-semibold text-amber-700 dark:text-amber-400 hover:underline flex items-center gap-1"
                  >
                    <span>{t("result.view_guide")}</span>
                    <ExternalLink size={12} />
                  </Link>
                </div>
              </div>
            );
          })}

          {/* Feedback Prompt if confidence is low */}
          {displayData.feedback_prompt && (
            <div className="sf-glass-card p-4 flex items-center justify-between gap-4 text-xs">
              <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
                <span className="text-base">💡</span>
                <span>{displayData.feedback_prompt}</span>
              </div>
              <Link
                to={`/feedback?session_id=${sessionId ?? ""}`}
                className="sf-btn sf-btn--ghost sf-btn--sm shrink-0"
              >
                {t("result.give_feedback")}
              </Link>
            </div>
          )}
        </div>
      ) : (
        /* Inconclusive / No Clear Match */
        <div className="sf-glass-card p-8 sm:p-10 text-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mx-auto text-3xl">
            🌱
          </div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
            {t("result.no_match_title")}
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 max-w-md mx-auto leading-relaxed">
            {t("result.no_match_desc")}
          </p>
          <div className="flex flex-wrap justify-center gap-3 pt-2">
            <Link
              to={`/feedback?session_id=${sessionId ?? ""}&subject=${encodeURIComponent("Inconclusive diagnosis consultation")}`}
              className="sf-btn sf-btn--primary"
            >
              <MessageSquare size={16} />
              <span>{t("result.consult_expert")}</span>
            </Link>
            <Link to="/check" className="sf-btn sf-btn--ghost">
              <RotateCcw size={16} />
              <span>{t("result.try_again")}</span>
            </Link>
          </div>
        </div>
      )}

      {/* Answered Symptoms Log */}
      {session && session.selected_symptoms.length > 0 && (
        <div className="sf-glass-card p-4 sm:p-5 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
            {t("result.your_answers_title")} ({session.selected_symptoms.length})
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
            {session.selected_symptoms.map((s) => (
              <div
                key={s.symptom_id}
                className="p-2 rounded-lg bg-slate-50 dark:bg-stone-900/70 border border-slate-200/60 dark:border-slate-800 flex items-center gap-2 text-xs"
              >
                <span>{s.answer === "yes" ? "✅" : s.answer === "no" ? "❌" : "❓"}</span>
                <span className="font-mono text-slate-700 dark:text-slate-300 truncate">
                  {s.symptom_code}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bottom Action Footer */}
      <div className="pt-6 border-t border-slate-200/80 dark:border-slate-800 flex flex-wrap justify-between items-center gap-4">
        <Link to="/check" className="sf-btn sf-btn--secondary flex items-center gap-1.5">
          <RotateCcw size={16} />
          <span>{t("result.start_new")}</span>
        </Link>

        <Link
          to={`/feedback?session_id=${sessionId ?? ""}`}
          className="sf-btn sf-btn--ghost flex items-center gap-1.5"
        >
          <MessageSquare size={16} />
          <span>{t("result.give_feedback")}</span>
        </Link>
      </div>
    </div>
  );
}
