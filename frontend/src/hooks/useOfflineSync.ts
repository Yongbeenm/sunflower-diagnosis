import { useState, useEffect, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  getPendingDiagnoses,
  getPendingCount,
  removeSyncedDiagnosis,
  updateDiagnosisStatus,
  type PendingDiagnosisItem,
} from "@/lib/offlineQueue";
import { submitDiagnosis } from "@/features/diagnosis/api";

export interface OfflineSyncState {
  isOnline: boolean;
  pendingCount: number;
  isSyncing: boolean;
  lastSyncError: string | null;
  syncPendingData: () => Promise<void>;
}

export function useOfflineSync(): OfflineSyncState {
  const queryClient = useQueryClient();
  const [isOnline, setIsOnline] = useState<boolean>(
    typeof navigator !== "undefined" ? navigator.onLine : true,
  );
  const [pendingCount, setPendingCount] = useState<number>(0);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [lastSyncError, setLastSyncError] = useState<string | null>(null);

  const refreshCount = useCallback(async () => {
    try {
      const count = await getPendingCount();
      setPendingCount(count);
    } catch {
      // Ignore initial IndexedDB error
    }
  }, []);

  const syncPendingData = useCallback(async () => {
    if (typeof navigator !== "undefined" && !navigator.onLine) return;
    if (isSyncing) return;

    setIsSyncing(true);
    setLastSyncError(null);

    try {
      const pendingItems: PendingDiagnosisItem[] = await getPendingDiagnoses();
      if (pendingItems.length === 0) {
        setIsSyncing(false);
        return;
      }

      for (const item of pendingItems) {
        try {
          await updateDiagnosisStatus(item.id, "syncing");

          // Send to FastAPI backend
          await submitDiagnosis(item.answers, item.locale);

          // Remove on successful sync
          await removeSyncedDiagnosis(item.id);
        } catch (err: unknown) {
          const errMsg = err instanceof Error ? err.message : "Sync failed";
          await updateDiagnosisStatus(item.id, "failed", errMsg);
          setLastSyncError(errMsg);
        }
      }

      // Invalidate relevant React Query caches to show synced history in UI
      await queryClient.invalidateQueries({ queryKey: ["diagnosisHistory"] });
      await queryClient.invalidateQueries({ queryKey: ["diagnosisSession"] });
    } catch (err: unknown) {
      setLastSyncError(err instanceof Error ? err.message : "General sync error");
    } finally {
      setIsSyncing(false);
      await refreshCount();
    }
  }, [isSyncing, queryClient, refreshCount]);

  useEffect(() => {
    void refreshCount();

    const handleOnline = () => {
      setIsOnline(true);
      void syncPendingData();
    };

    const handleOffline = () => {
      setIsOnline(false);
      void refreshCount();
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, [syncPendingData, refreshCount]);

  return {
    isOnline,
    pendingCount,
    isSyncing,
    lastSyncError,
    syncPendingData,
  };
}

