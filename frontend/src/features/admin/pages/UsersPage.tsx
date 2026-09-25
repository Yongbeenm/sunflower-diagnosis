import type React from "react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Users,
  Shield,
  UserCheck,
  UserX,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  AlertCircle,
  Loader2,
  Calendar,
  Mail,
} from "lucide-react";
import { useAdminUsers, useAdminRoles, useUpdateAdminUser } from "../hooks";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import type { AdminUserItem } from "@/types/api";

export function UsersPage(): React.JSX.Element {
  const { t } = useTranslation();
  const [page, setPage] = useState<number>(1);
  const pageSize = 15;

  const {
    data: usersData,
    isLoading: isLoadingUsers,
    isError: isUsersError,
  } = useAdminUsers(page, pageSize);
  const { data: rolesData, isLoading: isLoadingRoles } = useAdminRoles();
  const updateUserMutation = useUpdateAdminUser();

  // State for status toggle confirm dialog
  const [pendingDeactivateUser, setPendingDeactivateUser] = useState<AdminUserItem | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleRoleChange = async (user: AdminUserItem, newRoleId: number) => {
    setErrorMessage(null);
    try {
      await updateUserMutation.mutateAsync({
        userId: user.id,
        data: { role_id: newRoleId },
      });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : t("admin.users_update_error");
      setErrorMessage(message);
    }
  };

  const handleToggleActive = async (user: AdminUserItem) => {
    setErrorMessage(null);
    if (user.is_active) {
      // Prompt confirmation before deactivating
      setPendingDeactivateUser(user);
    } else {
      // Reactivate directly
      try {
        await updateUserMutation.mutateAsync({
          userId: user.id,
          data: { is_active: true },
        });
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : t("admin.users_update_error");
        setErrorMessage(message);
      }
    }
  };

  const confirmDeactivate = async () => {
    if (!pendingDeactivateUser) return;
    setErrorMessage(null);
    try {
      await updateUserMutation.mutateAsync({
        userId: pendingDeactivateUser.id,
        data: { is_active: false },
      });
      setPendingDeactivateUser(null);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : t("admin.users_update_error");
      setErrorMessage(message);
    }
  };

  const totalPages = usersData ? Math.ceil(usersData.total / pageSize) : 1;
  const roles = rolesData?.items ?? [];

  return (
    <div className="sf-admin-page max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl p-6 sm:p-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/15 dark:bg-amber-400/15 flex items-center justify-center text-amber-700 dark:text-amber-400">
              <Users className="w-5 h-5" />
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
              {t("admin.users_title")}
            </h1>
            {usersData && (
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-500/15 text-amber-800 dark:text-amber-300 border border-amber-500/20">
                {usersData.total} {t("admin.users_total", { defaultValue: "users" })}
              </span>
            )}
          </div>
          <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300 mt-1">
            {t("admin.users_subtitle")}
          </p>
        </div>
      </div>

      {errorMessage && (
        <div className="sf-alert sf-alert--danger flex items-center gap-2" role="alert">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {isLoadingUsers || isLoadingRoles ? (
        <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl flex flex-col items-center justify-center py-16 text-center">
          <Loader2 className="w-8 h-8 animate-spin text-amber-600 dark:text-amber-400" />
          <p className="mt-3 text-sm font-medium text-gray-600 dark:text-gray-300">
            {t("common.loading")}
          </p>
        </div>
      ) : isUsersError || !usersData ? (
        <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md border border-stone-200/80 dark:border-white/10 shadow-lg rounded-2xl p-6">
          <div className="sf-alert sf-alert--danger flex items-center gap-2" role="alert">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{t("admin.users_load_error")}</span>
          </div>
        </div>
      ) : (
        <div className="sf-glass-card bg-white/85 dark:bg-[#2A3420]/80 backdrop-blur-md p-0 overflow-hidden shadow-lg border border-stone-200/80 dark:border-white/10 rounded-2xl">
          <div className="overflow-x-auto">
            <table className="sf-table w-full">
              <thead>
                <tr className="bg-stone-100/80 dark:bg-[#1E2615]/90 border-b border-stone-200/80 dark:border-white/10">
                  <th className="font-semibold text-xs uppercase tracking-wider text-gray-600 dark:text-gray-300 py-3.5 px-4">
                    {t("admin.users_col_username")}
                  </th>
                  <th className="font-semibold text-xs uppercase tracking-wider text-gray-600 dark:text-gray-300 py-3.5 px-4">
                    {t("admin.users_col_email")}
                  </th>
                  <th className="font-semibold text-xs uppercase tracking-wider text-gray-600 dark:text-gray-300 py-3.5 px-4">
                    {t("admin.users_col_role")}
                  </th>
                  <th className="font-semibold text-xs uppercase tracking-wider text-gray-600 dark:text-gray-300 py-3.5 px-4">
                    {t("admin.users_col_status")}
                  </th>
                  <th className="font-semibold text-xs uppercase tracking-wider text-gray-600 dark:text-gray-300 py-3.5 px-4">
                    {t("admin.users_col_created")}
                  </th>
                  <th className="font-semibold text-xs uppercase tracking-wider text-gray-600 dark:text-gray-300 py-3.5 px-4 text-right">
                    {t("admin.users_col_actions")}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-200/70 dark:divide-white/10">
                {usersData.items.length === 0 ? (
                  <tr>
                    <td
                      colSpan={6}
                      className="text-center py-12 text-gray-500 dark:text-gray-400 text-sm"
                    >
                      {t("admin.users_none_found")}
                    </td>
                  </tr>
                ) : (
                  usersData.items.map((u) => (
                    <tr key={u.id} className="transition-colors hover:bg-amber-500/5 dark:hover:bg-white/5">
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2.5">
                          <div className="w-8 h-8 rounded-full bg-amber-500/15 dark:bg-amber-400/15 text-amber-700 dark:text-amber-400 flex items-center justify-center font-bold text-xs uppercase">
                            {u.username.slice(0, 2)}
                          </div>
                          <span className="font-semibold text-sm text-gray-900 dark:text-white">
                            {u.username}
                          </span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-sm text-gray-600 dark:text-gray-300">
                        <div className="flex items-center gap-1.5">
                          <Mail className="w-3.5 h-3.5 opacity-60" />
                          <span>{u.email}</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="relative inline-flex items-center">
                          <Shield className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 absolute left-2.5 pointer-events-none z-10" />
                          <select
                            className="appearance-none text-xs font-semibold pl-8 pr-8 py-1.5 rounded-full bg-white dark:bg-[#182010] border border-stone-200 dark:border-white/10 text-stone-800 dark:text-stone-100 cursor-pointer hover:border-amber-500/80 focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-500/20 shadow-xs transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            value={u.role_id}
                            disabled={updateUserMutation.isPending}
                            onChange={(e) => void handleRoleChange(u, Number(e.target.value))}
                            aria-label={t("admin.users_change_role_label", { username: u.username })}
                          >
                            {roles.map((r) => (
                              <option
                                key={r.id}
                                value={r.id}
                                className="bg-white dark:bg-[#182010] text-stone-900 dark:text-stone-100"
                              >
                                {r.name}
                              </option>
                            ))}
                          </select>
                          <ChevronDown className="w-3.5 h-3.5 text-stone-400 dark:text-stone-400 absolute right-2.5 pointer-events-none" />
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`sf-badge inline-flex items-center gap-1 text-xs px-2.5 py-0.5 font-medium rounded-full ${
                            u.is_active
                              ? "sf-badge--success bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20"
                              : "sf-badge--neutral bg-slate-500/10 text-slate-500 border border-slate-500/20"
                          }`}
                        >
                          <span className={`w-1.5 h-1.5 rounded-full ${u.is_active ? "bg-amber-500" : "bg-slate-400"}`} />
                          {u.is_active
                            ? t("admin.users_status_active")
                            : t("admin.users_status_inactive")}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-xs text-gray-600 dark:text-gray-300 whitespace-nowrap">
                        <div className="flex items-center gap-1.5">
                          <Calendar className="w-3.5 h-3.5 opacity-60" />
                          <span>{new Date(u.created_at).toLocaleDateString()}</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-right whitespace-nowrap">
                        <button
                          type="button"
                          className={`sf-btn sf-btn--sm inline-flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-medium transition-all ${
                            u.is_active
                              ? "text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 border border-rose-200 dark:border-rose-900/50"
                              : "text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50"
                          }`}
                          disabled={updateUserMutation.isPending}
                          onClick={() => void handleToggleActive(u)}
                        >
                          {u.is_active ? (
                            <>
                              <UserX className="w-3.5 h-3.5" />
                              <span>{t("admin.users_btn_deactivate")}</span>
                            </>
                          ) : (
                            <>
                              <UserCheck className="w-3.5 h-3.5" />
                              <span>{t("admin.users_btn_activate")}</span>
                            </>
                          )}
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex flex-col sm:flex-row justify-between items-center gap-3 p-4 border-t border-stone-200/80 dark:border-white/10 bg-stone-50/60 dark:bg-[#1E2615]/50">
              <span className="text-xs text-gray-600 dark:text-gray-300">
                {t("admin.pagination_showing_pages", { page, totalPages, total: usersData.total })}
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  className="sf-btn sf-btn--outline sf-btn--sm inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg"
                  disabled={page <= 1 || updateUserMutation.isPending}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  <span>{t("admin.pagination_prev")}</span>
                </button>
                <button
                  type="button"
                  className="sf-btn sf-btn--outline sf-btn--sm inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg"
                  disabled={page >= totalPages || updateUserMutation.isPending}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                >
                  <span>{t("admin.pagination_next")}</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Confirmation Dialog for Deactivation */}
      <ConfirmDialog
        isOpen={Boolean(pendingDeactivateUser)}
        title={t("admin.users_deactivate_confirm_title")}
        message={t("admin.users_deactivate_confirm_message", {
          username: pendingDeactivateUser?.username ?? "",
        })}
        confirmLabel={t("admin.users_btn_deactivate")}
        cancelLabel={t("common.cancel")}
        variant="danger"
        isLoading={updateUserMutation.isPending}
        onConfirm={() => void confirmDeactivate()}
        onCancel={() => setPendingDeactivateUser(null)}
      />
    </div>
  );
}

