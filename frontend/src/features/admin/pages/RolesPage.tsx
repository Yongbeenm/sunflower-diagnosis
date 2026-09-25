import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import {
  ShieldCheck,
  Key,
  Save,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Lock,
} from "lucide-react";
import { useAdminRoles, useUpdateRolePermissions } from "../hooks";

export function RolesPage(): React.JSX.Element {
  const { t } = useTranslation();
  const { data: rolesData, isLoading, isError } = useAdminRoles();
  const updateRolePermissionsMutation = useUpdateRolePermissions();

  // Local state for role -> Set of permission codes
  const [rolePermissions, setRolePermissions] = useState<Record<number, Set<string>>>({});
  const [savingRoleId, setSavingRoleId] = useState<number | null>(null);
  const [statusMessage, setStatusMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  // Sync server data into local state when loaded
  useEffect(() => {
    if (rolesData) {
      const map: Record<number, Set<string>> = {};
      for (const role of rolesData.items) {
        map[role.id] = new Set(role.permissions);
      }
      setRolePermissions(map);
    }
  }, [rolesData]);

  const handleTogglePermission = (roleId: number, permissionCode: string) => {
    setStatusMessage(null);
    setRolePermissions((prev) => {
      const current = new Set(prev[roleId] ?? []);
      if (current.has(permissionCode)) {
        current.delete(permissionCode);
      } else {
        current.add(permissionCode);
      }
      return {
        ...prev,
        [roleId]: current,
      };
    });
  };

  const handleSaveRole = async (roleId: number) => {
    setStatusMessage(null);
    setSavingRoleId(roleId);
    try {
      const codes = Array.from(rolePermissions[roleId] ?? []);
      await updateRolePermissionsMutation.mutateAsync({
        roleId,
        permissionCodes: codes,
      });
      setStatusMessage({
        type: "success",
        text: t("admin.roles_save_success"),
      });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : t("admin.roles_save_error");
      setStatusMessage({
        type: "error",
        text: message,
      });
    } finally {
      setSavingRoleId(null);
    }
  };

  const isRoleDirty = (roleId: number): boolean => {
    if (!rolesData) return false;
    const serverRole = rolesData.items.find((r) => r.id === roleId);
    if (!serverRole) return false;

    const serverSet = new Set(serverRole.permissions);
    const localSet = rolePermissions[roleId] ?? new Set();

    if (serverSet.size !== localSet.size) return true;
    for (const code of localSet) {
      if (!serverSet.has(code)) return true;
    }
    return false;
  };

  // Group permissions by prefix / domain
  const groupPermissions = () => {
    if (!rolesData) return {};
    const groups: Record<string, typeof rolesData.permissions> = {};

    for (const perm of rolesData.permissions) {
      const domain: string = perm.code.includes(":")
        ? (perm.code.split(":")[0] ?? "general")
        : "general";
      const currentList = groups[domain] ?? [];
      currentList.push(perm);
      groups[domain] = currentList;
    }
    return groups;
  };

  const permGroups = groupPermissions();
  const roles = rolesData?.items ?? [];

  return (
    <div className="sf-admin-page max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl p-6 sm:p-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/15 dark:bg-amber-400/15 flex items-center justify-center text-amber-700 dark:text-amber-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
              {t("admin.roles_title")}
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300 mt-1">
            {t("admin.roles_subtitle")}
          </p>
        </div>
      </div>

      {statusMessage && (
        <div
          className={`sf-alert ${
            statusMessage.type === "success" ? "sf-alert--success" : "sf-alert--danger"
          } flex items-center gap-2`}
          role="alert"
        >
          {statusMessage.type === "success" ? (
            <CheckCircle2 className="w-5 h-5 text-amber-600 shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}

      {isLoading ? (
        <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl flex flex-col items-center justify-center py-16 text-center">
          <Loader2 className="w-8 h-8 animate-spin text-amber-600 dark:text-amber-400" />
          <p className="mt-3 text-sm font-medium text-gray-600 dark:text-gray-300">
            {t("common.loading")}
          </p>
        </div>
      ) : isError || !rolesData ? (
        <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl p-6">
          <div className="sf-alert sf-alert--danger flex items-center gap-2" role="alert">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{t("admin.roles_load_error")}</span>
          </div>
        </div>
      ) : (
        <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md p-0 overflow-hidden shadow-lg border border-stone-200/80 dark:border-white/10 rounded-2xl">
          <div className="overflow-x-auto">
            <table className="sf-table sf-matrix-table w-full">
              <thead>
                <tr className="bg-stone-100/80 dark:bg-[#1E2615]/90 border-b border-stone-200/80 dark:border-white/10">
                  <th className="w-2/5 font-semibold text-xs uppercase tracking-wider text-gray-600 dark:text-gray-200 py-4 px-6 text-left">
                    <div className="flex items-center gap-2">
                      <Key className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                      <span>{t("admin.roles_col_permission")}</span>
                    </div>
                  </th>
                  {roles.map((role) => {
                    const dirty = isRoleDirty(role.id);
                    const isSaving = savingRoleId === role.id;
                    return (
                      <th
                        key={role.id}
                        className="py-4 px-4 text-center min-w-[140px] border-l border-stone-200/80 dark:border-white/10"
                      >
                        <div className="font-bold text-sm text-gray-900 dark:text-white capitalize">
                          {role.name}
                        </div>
                        <div className="mt-2 flex justify-center">
                          <button
                            type="button"
                            className={`sf-btn sf-btn--sm inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                              dirty
                                ? "bg-amber-600 hover:bg-amber-700 text-white shadow-sm ring-2 ring-amber-500/20"
                                : "opacity-40 cursor-not-allowed bg-stone-200 dark:bg-[#1E2615]/80 text-stone-500 dark:text-stone-400 border border-transparent dark:border-white/5"
                            }`}
                            disabled={!dirty || isSaving}
                            onClick={() => void handleSaveRole(role.id)}
                          >
                            {isSaving ? (
                              <>
                                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                <span>{t("common.saving")}</span>
                              </>
                            ) : (
                              <>
                                <Save className="w-3.5 h-3.5" />
                                <span>{t("common.save")}</span>
                              </>
                            )}
                          </button>
                        </div>
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-200/70 dark:divide-white/10">
                {Object.entries(permGroups).map(([group, permissions]) => (
                  <React.Fragment key={group}>
                    <tr className="bg-stone-100/50 dark:bg-[#182010]/90">
                      <td
                        colSpan={roles.length + 1}
                        className="font-bold text-xs uppercase tracking-wider text-amber-800 dark:text-amber-300 py-2.5 px-6"
                      >
                        <div className="flex items-center gap-2">
                          <Lock className="w-3.5 h-3.5" />
                          <span>
                            {group} {t("admin.roles_module_suffix")}
                          </span>
                        </div>
                      </td>
                    </tr>
                    {permissions.map((perm) => (
                      <tr
                        key={perm.id ?? perm.code}
                        className="transition-colors hover:bg-amber-500/5 dark:hover:bg-white/5"
                      >
                        <td className="py-3 px-6">
                          <div className="font-mono font-semibold text-xs text-gray-900 dark:text-gray-100 bg-white dark:bg-[#182010] px-2 py-0.5 rounded inline-block border border-stone-200 dark:border-white/10">
                            {perm.code}
                          </div>
                          {perm.description && (
                            <div className="text-xs text-gray-600 dark:text-gray-300 mt-1">
                              {perm.description}
                            </div>
                          )}
                        </td>
                        {roles.map((role) => {
                          const isChecked = rolePermissions[role.id]?.has(perm.code) ?? false;
                          return (
                            <td
                              key={role.id}
                              className="text-center py-3 px-4 border-l border-stone-200/70 dark:border-white/10"
                            >
                              <input
                                type="checkbox"
                                checked={isChecked}
                                onChange={() => handleTogglePermission(role.id, perm.code)}
                                aria-label={`${role.name} - ${perm.code}`}
                                className="w-4 h-4 text-amber-600 rounded border-stone-300 dark:border-stone-600 focus:ring-amber-500 cursor-pointer accent-amber-600"
                              />
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

