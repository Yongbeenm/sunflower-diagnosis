import React from "react";
import { useTranslation } from "react-i18next";
import { WifiOff, RefreshCw, CheckCircle2, AlertTriangle } from "lucide-react";
import { useOfflineSync } from "@/hooks/useOfflineSync";

export function OfflineBanner(): React.JSX.Element | null {
  const { t } = useTranslation();
  const { isOnline, pendingCount, isSyncing, syncPendingData, lastSyncError } =
    useOfflineSync();

  // If online with no items waiting, hide the banner
  if (isOnline && pendingCount === 0 && !isSyncing && !lastSyncError) {
    return null;
  }

  return (
    <div
      role="status"
      aria-live="polite"
      className="sticky top-16 z-40 w-full px-4 py-2 transition-all duration-300"
    >
      <div
        className={`max-w-7xl mx-auto px-4 py-2.5 rounded-xl backdrop-blur-md border shadow-md flex items-center justify-between gap-3 text-xs sm:text-sm font-medium ${
          !isOnline
            ? "bg-amber-500/15 dark:bg-[#342A15]/90 border-amber-500/40 text-amber-900 dark:text-amber-200"
            : lastSyncError
            ? "bg-rose-500/15 dark:bg-[#341818]/90 border-rose-500/40 text-rose-900 dark:text-rose-200"
            : "bg-emerald-500/15 dark:bg-[#18301E]/90 border-emerald-500/40 text-emerald-900 dark:text-emerald-200"
        }`}
      >
        <div className="flex items-center gap-2.5">
          {!isOnline ? (
            <WifiOff className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
          ) : lastSyncError ? (
            <AlertTriangle className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />
          ) : (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
          )}

          <span>
            {!isOnline
              ? t("offline.banner_offline_mode")
              : lastSyncError
              ? t("offline.sync_error", { error: lastSyncError })
              : t("offline.online_ready")}
          </span>

          {pendingCount > 0 && (
            <span className="px-2 py-0.5 rounded-full bg-amber-500/20 dark:bg-amber-400/20 text-amber-950 dark:text-amber-300 font-bold text-xs border border-amber-500/30">
              {pendingCount}{" "}
              {pendingCount === 1
                ? t("offline.pending_report_single")
                : t("offline.pending_reports")}
            </span>
          )}
        </div>

        {isOnline && pendingCount > 0 && (
          <button
            type="button"
            onClick={() => void syncPendingData()}
            disabled={isSyncing}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-amber-600 hover:bg-amber-700 text-white font-semibold transition-all disabled:opacity-50 cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? "animate-spin" : ""}`} />
            <span>
              {isSyncing ? t("common.saving") : t("common.retry")}
            </span>
          </button>
        )}
      </div>
    </div>
  );
}

