import type React from "react";
import { useTranslation } from "react-i18next";
import { X, Sparkles, ShieldCheck, Smartphone, Languages } from "lucide-react";

interface AboutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AboutModal({ isOpen, onClose }: AboutModalProps): React.JSX.Element | null {
  const { t } = useTranslation();

  if (!isOpen) return null;

  return (
    <div
      className="sf-modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="about-modal-title"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="sf-modal-sheet" style={{ maxWidth: "36rem", padding: "1.75rem" }}>
        <div className="flex items-center justify-between pb-4 border-b border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center gap-2.5">
            <span className="text-2xl" aria-hidden="true">
              🌻
            </span>
            <div>
              <h2
                id="about-modal-title"
                className="text-lg font-bold text-slate-900 dark:text-slate-100"
              >
                {t("about.title")}
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">{t("about.subtitle")}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            aria-label={t("about.close")}
          >
            <X size={20} />
          </button>
        </div>

        <div className="py-4 space-y-4 text-xs sm:text-sm text-slate-700 dark:text-slate-300">
          <p className="leading-relaxed">{t("about.description")}</p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-2">
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
              <Sparkles size={18} className="text-amber-500 mb-1.5" />
              <div className="font-bold text-slate-900 dark:text-slate-100 mb-0.5 text-xs">
                {t("about.feature1_title")}
              </div>
              <div className="text-[0.7rem] text-slate-500 leading-snug">
                {t("about.feature1_desc")}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
              <Smartphone size={18} className="text-emerald-500 mb-1.5" />
              <div className="font-bold text-slate-900 dark:text-slate-100 mb-0.5 text-xs">
                {t("about.feature2_title")}
              </div>
              <div className="text-[0.7rem] text-slate-500 leading-snug">
                {t("about.feature2_desc")}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
              <Languages size={18} className="text-blue-500 mb-1.5" />
              <div className="font-bold text-slate-900 dark:text-slate-100 mb-0.5 text-xs">
                {t("about.feature3_title")}
              </div>
              <div className="text-[0.7rem] text-slate-500 leading-snug">
                {t("about.feature3_desc")}
              </div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-amber-50/70 dark:bg-amber-950/40 border border-amber-200/80 dark:border-amber-900/60 flex items-start gap-2 text-xs">
            <ShieldCheck size={16} className="text-amber-600 shrink-0 mt-0.5" />
            <div className="leading-snug text-amber-900 dark:text-amber-200">
              <strong>{t("about.disclaimer_title")}:</strong> {t("about.disclaimer_desc")}
            </div>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-200/80 dark:border-slate-800 flex justify-end">
          <button type="button" onClick={onClose} className="sf-btn sf-btn--primary sf-btn--sm">
            {t("about.close")}
          </button>
        </div>
      </div>
    </div>
  );
}
