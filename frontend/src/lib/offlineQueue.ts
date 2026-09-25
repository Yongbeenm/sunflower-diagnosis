import { openDB, type DBSchema, type IDBPDatabase } from "idb";
import type { Answer } from "@/types/api";

export interface PendingDiagnosisItem {
  id: string; // Unique client-generated UUID
  createdAt: number;
  locale: string;
  answers: Record<number, Answer>;
  photoBase64?: string; // Stored offline base64 image
  notes?: string;
  status: "pending" | "syncing" | "failed";
  retryCount: number;
  errorMessage?: string;
}

interface SunflowerDB extends DBSchema {
  pending_diagnoses: {
    key: string;
    value: PendingDiagnosisItem;
    indexes: {
      "by-status": string;
      "by-created": number;
    };
  };
}

const DB_NAME = "sunflower-offline-db";
const DB_VERSION = 1;

let dbPromise: Promise<IDBPDatabase<SunflowerDB>> | null = null;

function getDB(): Promise<IDBPDatabase<SunflowerDB>> {
  if (!dbPromise) {
    dbPromise = openDB<SunflowerDB>(DB_NAME, DB_VERSION, {
      upgrade(db) {
        if (!db.objectStoreNames.contains("pending_diagnoses")) {
          const store = db.createObjectStore("pending_diagnoses", {
            keyPath: "id",
          });
          store.createIndex("by-status", "status");
          store.createIndex("by-created", "createdAt");
        }
      },
    });
  }
  return dbPromise;
}

/** Enqueue a diagnosis session for later synchronization */
export async function enqueueOfflineDiagnosis(
  payload: Omit<PendingDiagnosisItem, "id" | "createdAt" | "status" | "retryCount">,
): Promise<PendingDiagnosisItem> {
  const db = await getDB();
  const item: PendingDiagnosisItem = {
    ...payload,
    id: typeof crypto !== "undefined" && crypto.randomUUID
      ? crypto.randomUUID()
      : `offline_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
    createdAt: Date.now(),
    status: "pending",
    retryCount: 0,
  };

  await db.put("pending_diagnoses", item);
  return item;
}

/** Retrieve all pending items */
export async function getPendingDiagnoses(): Promise<PendingDiagnosisItem[]> {
  const db = await getDB();
  return db.getAllFromIndex("pending_diagnoses", "by-status", "pending");
}

/** Get total count of unsynced items */
export async function getPendingCount(): Promise<number> {
  const db = await getDB();
  return db.countFromIndex("pending_diagnoses", "by-status", "pending");
}

/** Mark an item status (e.g. syncing or failed) */
export async function updateDiagnosisStatus(
  id: string,
  status: PendingDiagnosisItem["status"],
  errorMessage?: string,
): Promise<void> {
  const db = await getDB();
  const item = await db.get("pending_diagnoses", id);
  if (item) {
    item.status = status;
    item.retryCount += 1;
    if (errorMessage) item.errorMessage = errorMessage;
    await db.put("pending_diagnoses", item);
  }
}

/** Remove an item once successfully synced to the backend */
export async function removeSyncedDiagnosis(id: string): Promise<void> {
  const db = await getDB();
  await db.delete("pending_diagnoses", id);
}

/** Clear all stored offline data */
export async function clearAllPendingDiagnoses(): Promise<void> {
  const db = await getDB();
  await db.clear("pending_diagnoses");
}

