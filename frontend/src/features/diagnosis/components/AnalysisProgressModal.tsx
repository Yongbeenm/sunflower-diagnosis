import type React from "react";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Check, Loader2, Sparkles, ShieldCheck } from "lucide-react";

interface AnalysisProgressModalProps {
  isOpen: boolean;
  symptomCount: number;
  onComplete?: () => void;
}

export function AnalysisProgressModal({
  isOpen,
  symptomCount,
}: AnalysisProgressModalProps): React.JSX.Element | null {
  const { t } = useTranslation();
  const [activeStep, setActiveStep] = useState<number>(0);

  const steps = [
    {
      id: 0,
      label: t("analysis.step_received", { count: symptomCount }),
    },
    {
      id: 1,
      label: t("analysis.step_relationships"),
    },
    {
      id: 2,
      label: t("analysis.step_patterns"),
    },
    {
      id: 3,
      label: t("analysis.step_calculating"),
    },
    {
      id: 4,
      label: t("analysis.step_preparing"),
    },
  ];

  useEffect(() => {
    if (!isOpen) {
      setActiveStep(0);
      return;
    }

    // Advance smoothly through the visual steps
    const timer1 = setTimeout(() => setActiveStep(1), 350);
    const timer2 = setTimeout(() => setActiveStep(2), 750);
    const timer3 = setTimeout(() => setActiveStep(3), 1150);
    const timer4 = setTimeout(() => setActiveStep(4), 1550);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="sf-modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="analysis-modal-title"
    >
      <div
        className="sf-modal-sheet text-center"
        style={{
          maxWidth: "30rem",
          padding: "2rem 1.75rem",
          background: "var(--color-surface)",
        }}
      >
        {/* Animated AI Pulse Orb */}
        <div className="flex justify-center mb-5">
          <div className="sf-ai-orb">
            <Sparkles size={32} className="text-white drop-shadow-md" aria-hidden="true" />
          </div>
        </div>

        <h2
          id="analysis-modal-title"
          className="text-xl font-bold text-slate-900 dark:text-slate-50 mb-1"
        >
          {t("analysis.title")}
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-6">{t("analysis.subtitle")}</p>

        {/* Step Progress Checklist */}
        <div className="space-y-3 text-left max-w-xs mx-auto mb-6">
          {steps.map((step) => {
            const isFinished = activeStep > step.id;
            const isCurrent = activeStep === step.id;

            return (
              <div
                key={step.id}
                className="flex items-center gap-3 transition-opacity duration-300"
                style={{
                  opacity: isFinished || isCurrent ? 1 : 0.4,
                }}
              >
                <div
                  className="w-5 h-5 rounded-full flex items-center justify-center shrink-0 text-xs transition-colors duration-200"
                  style={{
                    backgroundColor: isFinished
                      ? "var(--color-secondary)"
                      : isCurrent
                        ? "var(--color-primary)"
                        : "var(--color-surface-raised)",
                    color: isFinished ? "white" : isCurrent ? "black" : "var(--color-text-muted)",
                    border: isFinished || isCurrent ? "none" : "1px solid var(--color-border)",
                  }}
                >
                  {isFinished ? (
                    <Check size={12} strokeWidth={3} />
                  ) : isCurrent ? (
                    <Loader2 size={12} className="animate-spin" />
                  ) : (
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                  )}
                </div>

                <span
                  className="text-xs font-medium"
                  style={{
                    color: isFinished
                      ? "var(--color-text)"
                      : isCurrent
                        ? "var(--color-text)"
                        : "var(--color-text-muted)",
                    fontWeight: isCurrent ? 600 : 500,
                  }}
                >
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>

        {/* Medical Safety UX Banner */}
        <div
          className="rounded-lg p-2.5 text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2 text-left"
          style={{
            background: "var(--color-surface-raised)",
            border: "1px solid var(--color-border)",
          }}
        >
          <ShieldCheck size={16} className="text-green-600 shrink-0" aria-hidden="true" />
          <span className="text-[0.72rem] leading-tight">{t("analysis.safety_notice")}</span>
        </div>
      </div>
    </div>
  );
}
