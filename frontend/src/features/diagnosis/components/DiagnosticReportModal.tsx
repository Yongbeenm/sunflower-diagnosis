import React, { useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Download,
  Share2,
  Printer,
  X,
  ShieldAlert,
  Sparkles,
  CheckCircle2,
  FileText,
  Loader2,
  CopyCheck,
} from "lucide-react";
import { generatePdfFromElement, shareDiagnosticReport } from "../utils/exportPdf";
import { useDiseaseDetail } from "@/features/diseases/hooks";
import type { DiagnosisResult, DiagnosisSessionDetail, DiseaseDetail } from "@/types/api";

interface DiagnosticReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  session: DiagnosisSessionDetail | null;
  results: DiagnosisResult[];
  diseaseDetail?: DiseaseDetail | null;
}

export function DiagnosticReportModal({
  isOpen,
  onClose,
  session,
  results,
  diseaseDetail: initialDetail,
}: DiagnosticReportModalProps): React.JSX.Element | null {
  const { t, i18n } = useTranslation();
  const reportRef = useRef<HTMLDivElement>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [shareStatus, setShareStatus] = useState<string | null>(null);

  const topResult = results.length > 0 ? results[0] : null;
  const secondaryResults = results.slice(1, 4);

  // Load detailed information for the top matched disease if not provided
  const { data: fetchedDetail, isLoading: isDetailLoading } = useDiseaseDetail(
    !initialDetail && topResult?.disease.slug ? topResult.disease.slug : "",
  );

  const diseaseDetail = initialDetail ?? fetchedDetail;

  if (!isOpen) return null;

  const reportId = session?.session_id || `SES-${Date.now().toString(36).toUpperCase()}`;
  const currentDate = new Date().toLocaleString(i18n.language === "km" ? "km-KH" : "en-US", {
    dateStyle: "full",
    timeStyle: "short",
  });

  const handleDownloadPdf = async () => {
    if (!reportRef.current || isExporting) return;
    setIsExporting(true);
    try {
      const fileName = `Sunflower_Report_${reportId}.pdf`;
      await generatePdfFromElement(reportRef.current, fileName);
    } catch (err) {
      console.error("PDF generation failed:", err);
    } finally {
      setIsExporting(false);
    }
  };

  const handleShare = async () => {
    if (!reportRef.current || isExporting) return;
    setIsExporting(true);
    try {
      const fileName = `Sunflower_Report_${reportId}.pdf`;
      const blob = await generatePdfFromElement(reportRef.current, fileName);

      const res = await shareDiagnosticReport({
        title: t("report.share_title"),
        text: t("report.share_text", {
          disease: topResult?.disease.name ?? "Diagnosis",
          confidence: Math.round((topResult?.confidence ?? 0) * 100),
        }),
        pdfBlob: blob,
        fileName,
      });

      if (res.success) {
        setShareStatus(
          res.method === "clipboard"
            ? t("report.share_success")
            : t("report.share_title"),
        );
        setTimeout(() => setShareStatus(null), 3000);
      }
    } catch (err) {
      console.error("Sharing failed:", err);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="report-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/70 backdrop-blur-sm overflow-y-auto animate-fadeIn"
    >
      <div className="relative w-full max-w-4xl bg-white dark:bg-[#1E2615] rounded-2xl shadow-2xl border border-stone-200/80 dark:border-white/10 flex flex-col max-h-[92vh] overflow-hidden">
        {/* Modal Top Bar */}
        <div className="p-4 sm:px-6 bg-stone-50/90 dark:bg-[#182010]/90 border-b border-stone-200/80 dark:border-white/10 flex items-center justify-between gap-3 shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-500/15 flex items-center justify-center text-amber-700 dark:text-amber-400">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h2 id="report-modal-title" className="text-sm sm:text-base font-bold text-gray-900 dark:text-white">
                {t("report.modal_title")}
              </h2>
              <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">
                {reportId}
              </span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => void handleShare()}
              disabled={isExporting}
              className="sf-btn sf-btn--secondary sf-btn--sm flex items-center gap-1.5 text-xs font-semibold cursor-pointer"
              title={t("report.btn_share")}
            >
              <Share2 size={14} />
              <span className="hidden sm:inline">{t("report.btn_share")}</span>
            </button>

            <button
              type="button"
              onClick={() => void handleDownloadPdf()}
              disabled={isExporting}
              className="sf-btn sf-btn--primary sf-btn--sm flex items-center gap-1.5 text-xs font-semibold cursor-pointer"
              title={t("report.btn_download_pdf")}
            >
              {isExporting ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <Download size={14} />
              )}
              <span>{t("report.btn_download_pdf")}</span>
            </button>

            <button
              type="button"
              onClick={() => window.print()}
              className="sf-btn sf-btn--secondary sf-btn--sm flex items-center gap-1 text-xs font-semibold cursor-pointer hidden md:flex"
              title={t("diseases.print")}
            >
              <Printer size={14} />
            </button>

            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 dark:hover:text-white hover:bg-stone-100 dark:hover:bg-white/5 transition-colors cursor-pointer"
              aria-label={t("common.close")}
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Share Status Toast */}
        {shareStatus && (
          <div className="bg-emerald-600 text-white px-4 py-2 text-xs font-medium flex items-center justify-center gap-2 animate-fadeIn">
            <CopyCheck size={14} />
            <span>{shareStatus}</span>
          </div>
        )}

        {/* Scrollable Printable Report Canvas (Strict High-DPI A4 Document) */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-8 bg-stone-100 dark:bg-[#12180C]/80">
          <div
            ref={reportRef}
            className="max-w-[780px] mx-auto bg-white text-slate-900 p-8 sm:p-10 rounded-xl shadow-lg border border-slate-200 print:shadow-none print:border-none print:m-0 print:p-0"
            style={{ color: "#0f172a" }}
          >
            {/* Branded Header */}
            <div className="border-b-2 border-amber-500 pb-5 mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className="text-4xl" aria-hidden="true">
                  🌻
                </span>
                <div>
                  <h1 className="text-xl sm:text-2xl font-black tracking-tight text-slate-950 uppercase font-sans">
                    {t("report.header_title")}
                  </h1>
                  <p className="text-xs text-amber-900 font-medium">
                    {t("report.header_subtitle")}
                  </p>
                </div>
              </div>

              <div className="text-right text-xs space-y-0.5 border-t sm:border-t-0 pt-2 sm:pt-0 border-slate-100 font-mono">
                <div>
                  <span className="text-slate-400 uppercase text-[0.65rem]">{t("report.doc_id")}: </span>
                  <span className="font-bold text-slate-800">{reportId}</span>
                </div>
                <div>
                  <span className="text-slate-400 uppercase text-[0.65rem]">{t("report.generated_at")}: </span>
                  <span className="text-slate-700">{currentDate}</span>
                </div>
              </div>
            </div>

            {/* Primary Diagnosis Box */}
            {topResult ? (
              <div className="mb-6 rounded-xl bg-gradient-to-br from-amber-500/10 via-amber-500/5 to-transparent border-2 border-amber-500/30 p-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
                  <div>
                    <div className="text-[0.65rem] font-bold uppercase tracking-widest text-amber-900 mb-0.5">
                      {t("report.primary_diagnosis")}
                    </div>
                    <h2 className="text-xl sm:text-2xl font-bold text-slate-950">
                      {topResult.disease.name}
                    </h2>
                    {diseaseDetail?.pathogen_type && (
                      <div className="text-xs text-slate-600 capitalize italic mt-0.5">
                        {diseaseDetail.pathogen_type} Pathogen
                      </div>
                    )}
                  </div>

                  {/* Confidence Rating Badge */}
                  <div className="inline-flex items-center gap-2 bg-amber-500 text-slate-950 px-4 py-2 rounded-xl font-bold shadow-xs shrink-0">
                    <Sparkles size={16} />
                    <div className="text-right">
                      <div className="text-[0.65rem] uppercase tracking-wider font-semibold opacity-80 leading-none">
                        {t("report.confidence_rating")}
                      </div>
                      <div className="text-lg font-black font-mono leading-tight">
                        {Math.round(topResult.confidence * 100)}%
                      </div>
                    </div>
                  </div>
                </div>

                {diseaseDetail?.description ? (
                  <p className="text-xs text-slate-700 leading-relaxed border-t border-amber-500/20 pt-3">
                    {diseaseDetail.description}
                  </p>
                ) : isDetailLoading ? (
                  <div className="text-xs text-slate-400 py-2">Loading details...</div>
                ) : null}
              </div>
            ) : null}

            {/* Differential / Alternative Matches */}
            {secondaryResults.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                  {t("report.differential_diagnoses")}
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  {secondaryResults.map((alt) => (
                    <div
                      key={alt.disease.slug || alt.disease.id}
                      className="p-2.5 rounded-lg border border-slate-200 bg-slate-50 flex items-center justify-between text-xs"
                    >
                      <span className="font-semibold text-slate-800 truncate pr-2">
                        {alt.disease.name}
                      </span>
                      <span className="font-mono font-bold text-amber-700 bg-amber-100 px-2 py-0.5 rounded text-[0.7rem] shrink-0">
                        {Math.round(alt.confidence * 100)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Observed Symptoms Checklist */}
            {session?.selected_symptoms && session.selected_symptoms.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                  {t("report.observed_symptoms")} ({session.selected_symptoms.length})
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                  {session.selected_symptoms.map((symp, idx) => (
                    <div
                      key={idx}
                      className="flex items-center gap-2 p-2 rounded-md bg-slate-50 border border-slate-100 text-xs text-slate-800"
                    >
                      <CheckCircle2 size={13} className="text-emerald-600 shrink-0" />
                      <span className="truncate">{symp.symptom_code}</span>
                      <span className="text-[0.65rem] uppercase font-bold text-emerald-800 bg-emerald-100 px-1.5 py-0.2 rounded ml-auto">
                        {symp.answer}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Treatment & Management Recommendations */}
            {diseaseDetail && (
              <div className="space-y-4 mb-6">
                {/* Chemical Treatment */}
                {diseaseDetail.treatment && (
                  <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/50">
                    <h4 className="text-xs font-bold text-blue-900 uppercase tracking-wide mb-1.5 flex items-center gap-1.5">
                      <span>🧪</span> {t("report.chemical_treatment")}
                    </h4>
                    <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-line">
                      {diseaseDetail.treatment}
                    </p>
                  </div>
                )}

                {/* Prevention Guidelines */}
                {diseaseDetail.prevention && (
                  <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/50">
                    <h4 className="text-xs font-bold text-amber-950 uppercase tracking-wide mb-1.5 flex items-center gap-1.5">
                      <span>🛡️</span> {t("report.prevention_guidelines")}
                    </h4>
                    <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-line">
                      {diseaseDetail.prevention}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Footer & Disclaimer */}
            <div className="border-t border-slate-200 pt-4 flex items-start gap-2.5 text-[0.7rem] text-slate-500 leading-relaxed">
              <ShieldAlert size={15} className="text-amber-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-slate-700">
                  {t("report.disclaimer_title")}:{" "}
                </span>
                {t("report.disclaimer_body")}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

