import type React from "react";
import { useTranslation } from "react-i18next";
import { AlertCircle, RotateCcw } from "lucide-react";
import { cn } from "@/lib/utils";

interface ErrorStateProps {
  className?: string;
  message?: string;
  onRetry?: () => void;
}

/**
 * Reusable error state with retry button.
 * Falls back to t("common.error") when no message is provided.
 */
export function ErrorState({ className, message, onRetry }: ErrorStateProps): React.JSX.Element {
  const { t } = useTranslation();

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center text-center p-8 sm:p-12 sf-glass-card space-y-4 border-rose-500/20",
        className,
      )}
      role="alert"
    >
      <div className="w-14 h-14 rounded-2xl bg-rose-500/10 dark:bg-rose-500/15 text-rose-600 dark:text-rose-400 flex items-center justify-center shadow-inner border border-rose-500/20">
        <AlertCircle size={28} />
      </div>

      <div className="space-y-1 max-w-sm">
        <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
          {t("common.error_title", "Something went wrong")}
        </h3>
        <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
          {message ?? t("common.error")}
        </p>
      </div>

      {onRetry && (
        <button
          type="button"
          className="sf-btn sf-btn--secondary sf-btn--sm flex items-center gap-2"
          onClick={onRetry}
        >
          <RotateCcw size={14} />
          <span>{t("common.retry")}</span>
        </button>
      )}
    </div>
  );
}
