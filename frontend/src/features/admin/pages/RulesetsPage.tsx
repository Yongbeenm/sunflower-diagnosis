import type React from "react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Sliders,
  CheckCircle2,
  Clock,
  AlertCircle,
  Loader2,
  History,
  Zap,
} from "lucide-react";
import { useRulesets, useActivateRuleset } from "../hooks";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import type { RulesetItem } from "@/types/api";

export function RulesetsPage(): React.JSX.Element {
  const { t } = useTranslation();
  const { data: rulesetsData, isLoading, isError } = useRulesets();
  const activateMutation = useActivateRuleset();

  const [selectedRuleset, setSelectedRuleset] = useState<RulesetItem | null>(null);
  const [pendingActivateRuleset, setPendingActivateRuleset] = useState<RulesetItem | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const rulesets = rulesetsData?.items ?? [];
  const activeRuleset = rulesets.find((r) => r.is_active) ?? null;

  // Selected or active ruleset for viewing details
  const currentView = selectedRuleset ?? activeRuleset ?? rulesets[0] ?? null;

  const handleConfirmActivate = async () => {
    if (!pendingActivateRuleset) return;
    setErrorMessage(null);
    try {
      await activateMutation.mutateAsync(pendingActivateRuleset.id);
      setPendingActivateRuleset(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : t("admin.rulesets_activate_error");
      setErrorMessage(msg);
    }
  };

  return (
    <div className="sf-admin-page max-w-7xl mx-auto">
      {/* Header */}
      <div className="sf-admin-page__header flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 dark:bg-amber-400/10 flex items-center justify-center text-amber-600 dark:text-amber-400">
              <Sliders className="w-5 h-5" />
            </div>
            <h1 className="sf-admin-page__title text-2xl font-bold tracking-tight">
              {t("admin.rulesets_title")}
            </h1>
          </div>
          <p className="sf-admin-page__desc text-sm text-[var(--color-text-muted)] mt-1">
            {t("admin.rulesets_subtitle")}
          </p>
        </div>
      </div>

      {errorMessage && (
        <div className="sf-alert sf-alert--danger flex items-center gap-2 mb-6" role="alert">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {isLoading ? (
        <div className="sf-card flex flex-col items-center justify-center py-16 text-center">
          <Loader2 className="w-8 h-8 animate-spin text-amber-600 dark:text-amber-400" />
          <p className="mt-3 text-sm font-medium text-[var(--color-text-muted)]">
            {t("common.loading")}
          </p>
        </div>
      ) : isError ? (
        <div className="sf-alert sf-alert--danger flex items-center gap-2" role="alert">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{t("admin.rulesets_load_error")}</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          {/* Ruleset List */}
          <div className="sf-card p-0 overflow-hidden shadow-sm border border-[var(--color-border)]">
            <div className="flex items-center gap-2 px-5 py-4 border-b border-[var(--color-border)] bg-[var(--color-bg-subtle)]/50">
              <History className="w-4 h-4 text-amber-600" />
              <h2 className="font-bold text-sm text-[var(--color-text)]">
                {t("admin.rulesets_version_history")}
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="sf-table w-full">
                <thead>
                  <tr>
                    <th className="font-semibold text-xs uppercase tracking-wider text-[var(--color-text-muted)] py-3 px-4">
                      {t("admin.rulesets_col_version")}
                    </th>
                    <th className="font-semibold text-xs uppercase tracking-wider text-[var(--color-text-muted)] py-3 px-4">
                      {t("admin.rulesets_col_algorithm")}
                    </th>
                    <th className="font-semibold text-xs uppercase tracking-wider text-[var(--color-text-muted)] py-3 px-4">
                      {t("admin.rulesets_col_status")}
                    </th>
                    <th className="font-semibold text-xs uppercase tracking-wider text-[var(--color-text-muted)] py-3 px-4 text-right">
                      {t("admin.rulesets_col_actions")}
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--color-border-subtle)]">
                  {rulesets.map((r) => {
                    const isCurrent = currentView?.id === r.id;
                    return (
                      <tr
                        key={r.id}
                        className={`transition-colors cursor-pointer ${
                          isCurrent
                            ? "bg-amber-500/10 dark:bg-amber-400/10 font-medium"
                            : "hover:bg-[var(--color-bg-subtle)]"
                        }`}
                        onClick={() => setSelectedRuleset(r)}
                      >
                        <td className="py-3 px-4">
                          <span className="font-mono font-bold text-xs text-[var(--color-text)]">
                            {r.version}
                          </span>
                          {r.published_at && (
                            <div className="text-[11px] text-[var(--color-text-muted)] mt-0.5">
                              {new Date(r.published_at).toLocaleDateString()}
                            </div>
                          )}
                        </td>
                        <td className="py-3 px-4 text-xs font-mono text-[var(--color-text-muted)]">
                          {r.algorithm}
                        </td>
                        <td className="py-3 px-4">
                          {r.is_active ? (
                            <span className="sf-badge sf-badge--success inline-flex items-center gap-1 text-xs px-2 py-0.5 font-medium rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400">
                              <CheckCircle2 className="w-3 h-3" />
                              <span>{t("admin.rulesets_status_active")}</span>
                            </span>
                          ) : (
                            <span className="sf-badge sf-badge--neutral inline-flex items-center gap-1 text-xs px-2 py-0.5 font-medium rounded-full bg-slate-500/10 text-slate-500">
                              <Clock className="w-3 h-3" />
                              <span>{t("admin.rulesets_status_inactive")}</span>
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-right whitespace-nowrap">
                          {!r.is_active && (
                            <button
                              type="button"
                              className="sf-btn sf-btn--outline-primary sf-btn--sm inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-lg border-amber-300 dark:border-amber-800 text-amber-700 dark:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-950/30"
                              disabled={activateMutation.isPending}
                              onClick={(e) => {
                                e.stopPropagation();
                                setPendingActivateRuleset(r);
                              }}
                            >
                              <Zap className="w-3 h-3" />
                              <span>{t("admin.rulesets_btn_activate")}</span>
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Ruleset Inspector & Diff */}
          {currentView && (
            <div className="sf-card p-6 shadow-sm border border-[var(--color-border)]">
              <div className="flex justify-between items-start mb-5 pb-4 border-b border-[var(--color-border)]">
                <div>
                  <div className="flex items-center gap-2.5">
                    <h2 className="text-xl font-bold font-mono tracking-tight text-[var(--color-text)]">
                      {currentView.version}
                    </h2>
                    {currentView.is_active ? (
                      <span className="sf-badge sf-badge--success inline-flex items-center gap-1 text-xs px-2.5 py-0.5 font-semibold rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>{t("admin.rulesets_status_active")}</span>
                      </span>
                    ) : (
                      <span className="sf-badge sf-badge--neutral inline-flex items-center gap-1 text-xs px-2.5 py-0.5 font-medium rounded-full bg-slate-500/10 text-slate-500">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{t("admin.rulesets_status_inactive")}</span>
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-[var(--color-text-muted)] mt-1.5 flex items-center gap-1.5">
                    <span>{t("admin.rulesets_algo_label")}:</span>
                    <code className="bg-slate-100 dark:bg-stone-800/80 px-2 py-0.5 rounded font-mono text-amber-600">
                      {currentView.algorithm}
                    </code>
                  </p>
                </div>
                {!currentView.is_active && (
                  <button
                    type="button"
                    className="sf-btn sf-btn--primary sf-btn--sm inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold shadow-sm"
                    disabled={activateMutation.isPending}
                    onClick={() => setPendingActivateRuleset(currentView)}
                  >
                    <Zap className="w-3.5 h-3.5" />
                    <span>{t("admin.rulesets_btn_activate")}</span>
                  </button>
                )}
              </div>

              <h3 className="text-sm font-bold text-[var(--color-text)] mb-3">
                {t("admin.rulesets_parameters_title")}
              </h3>

              <div className="space-y-2.5">
                {Object.entries(currentView.params).map(([key, val]) => {
                  const activeVal = activeRuleset?.params[key];
                  const hasChanged =
                    !currentView.is_active &&
                    activeRuleset &&
                    activeVal !== undefined &&
                    activeVal !== val;

                  return (
                    <div
                      key={key}
                      className={`flex justify-between items-center p-3 rounded-xl border transition-all ${
                        hasChanged
                          ? "bg-amber-500/10 border-amber-300 dark:border-amber-800"
                          : "bg-[var(--color-bg-subtle)]/70 border-[var(--color-border-subtle)]"
                      }`}
                    >
                      <div>
                        <span className="font-mono font-semibold text-xs text-[var(--color-text)]">
                          {key}
                        </span>
                        {hasChanged && (
                          <div className="text-[11px] text-amber-700 dark:text-amber-400 mt-0.5">
                            {t("admin.rulesets_active_val_was")}:{" "}
                            <code className="font-mono font-bold">{String(activeVal)}</code>
                          </div>
                        )}
                      </div>
                      <div className="font-mono font-bold text-sm text-[var(--color-text)]">
                        {String(val)}
                      </div>
                    </div>
                  );
                })}
              </div>

              {currentView.published_at && (
                <div className="mt-6 pt-4 border-t border-[var(--color-border-subtle)] text-xs text-[var(--color-text-muted)] flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 opacity-60" />
                  <span>
                    {t("admin.rulesets_published_meta", {
                      date: new Date(currentView.published_at).toLocaleString(),
                      author: currentView.published_by ?? t("admin.rulesets_author_system"),
                    })}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Confirmation Dialog */}
      <ConfirmDialog
        isOpen={Boolean(pendingActivateRuleset)}
        title={t("admin.rulesets_activate_confirm_title")}
        message={t("admin.rulesets_activate_confirm_message", {
          version: pendingActivateRuleset?.version ?? "",
        })}
        confirmLabel={t("admin.rulesets_btn_activate")}
        cancelLabel={t("common.cancel")}
        variant="warning"
        isLoading={activateMutation.isPending}
        onConfirm={() => void handleConfirmActivate()}
        onCancel={() => setPendingActivateRuleset(null)}
      />
    </div>
  );
}

