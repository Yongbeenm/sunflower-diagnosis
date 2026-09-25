import type React from "react";
import { useState, useEffect } from "react";
import { Link, Navigate } from "react-router";
import { useTranslation } from "react-i18next";
import {
  User as UserIcon,
  Mail,
  Shield,
  KeyRound,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Eye,
  EyeOff,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Layers,
  Stethoscope,
  Clock,
  LayoutDashboard,
} from "lucide-react";
import { useAuth } from "../context";

export function ProfilePage(): React.JSX.Element {
  const { t } = useTranslation();
  const { user, isLoading, updateProfile, hasPermission } = useAuth();

  const [activeTab, setActiveTab] = useState<"overview" | "details" | "security">("overview");

  // Account details form state
  const [username, setUsername] = useState<string>(user?.username ?? "");
  const [email, setEmail] = useState<string>(user?.email ?? "");
  const [detailsCurrentPassword, setDetailsCurrentPassword] = useState<string>("");
  const [isDetailsSaving, setIsDetailsSaving] = useState<boolean>(false);
  const [detailsSuccess, setDetailsSuccess] = useState<string | null>(null);
  const [detailsError, setDetailsError] = useState<string | null>(null);

  // Sync state when user object is loaded/updated
  useEffect(() => {
    if (user) {
      setUsername(user.username ?? "");
      setEmail(user.email ?? "");
    }
  }, [user]);

  // Security (password change) form state
  const [currentPassword, setCurrentPassword] = useState<string>("");
  const [newPassword, setNewPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [showCurrentPass, setShowCurrentPass] = useState<boolean>(false);
  const [showNewPass, setShowNewPass] = useState<boolean>(false);
  const [isPasswordSaving, setIsPasswordSaving] = useState<boolean>(false);
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  if (isLoading && !user) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-3" aria-busy="true">
        <Loader2 className="w-8 h-8 animate-spin text-amber-600 dark:text-amber-400" />
        <p className="text-sm text-gray-600 dark:text-gray-400">{t("common.loading")}</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: "/profile" }} />;
  }

  // Handle Account Details update
  const handleDetailsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setDetailsError(null);
    setDetailsSuccess(null);

    if (!detailsCurrentPassword) {
      setDetailsError(t("profile.error_current_password_required"));
      return;
    }

    const payload: { username?: string; email?: string; current_password: string } = {
      current_password: detailsCurrentPassword,
    };

    if (username.trim() && username !== user.username) {
      payload.username = username.trim();
    }
    if (email.trim() && email !== user.email) {
      payload.email = email.trim();
    }

    if (!payload.username && !payload.email) {
      setDetailsError(t("profile.error_no_changes"));
      return;
    }

    setIsDetailsSaving(true);
    try {
      await updateProfile(payload);
      setDetailsSuccess(t("profile.details_updated_success"));
      setDetailsCurrentPassword("");
    } catch (err: unknown) {
      setDetailsError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setIsDetailsSaving(false);
    }
  };

  // Handle Password Change
  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError(null);
    setPasswordSuccess(null);

    if (!currentPassword) {
      setPasswordError(t("profile.error_current_password_required"));
      return;
    }
    if (newPassword.length < 8) {
      setPasswordError(t("auth.error_password_min"));
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError(t("profile.error_password_mismatch"));
      return;
    }

    setIsPasswordSaving(true);
    try {
      await updateProfile({
        current_password: currentPassword,
        new_password: newPassword,
      });
      setPasswordSuccess(t("profile.password_updated_success"));
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: unknown) {
      setPasswordError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setIsPasswordSaving(false);
    }
  };

  const roleLabel =
    user.role === "admin"
      ? t("nav.admin")
      : user.role === "agronomist" || user.role === "expert"
        ? t("nav.expert")
        : t("profile.role_grower");

  return (
    <div className="max-w-4xl mx-auto space-y-6 sm:space-y-8 animate-fadeIn">
      {/* Profile Header Card */}
      <section className="sf-glass-card p-6 sm:p-8 relative overflow-hidden">
        {/* Subtle background glow */}
        <div
          className="absolute -top-16 -right-16 w-64 h-64 rounded-full bg-amber-400/15 dark:bg-amber-400/10 blur-3xl pointer-events-none"
          aria-hidden="true"
        />

        <div className="flex flex-col sm:flex-row items-center sm:items-start gap-5 relative z-10 text-center sm:text-left">
          {/* Avatar Orb */}
          <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-gradient-to-br from-amber-400 to-amber-600 text-stone-950 flex items-center justify-center font-extrabold text-2xl sm:text-3xl uppercase shadow-md shrink-0 border-2 border-white dark:border-stone-800">
            {user.username.slice(0, 2)}
          </div>

          {/* User Meta Info */}
          <div className="flex-1 min-w-0 space-y-2">
            <div className="flex flex-col sm:flex-row sm:items-center gap-2 justify-between">
              <div>
                <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-gray-900 dark:text-white leading-tight">
                  {user.username}
                </h1>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 flex items-center justify-center sm:justify-start gap-1.5 mt-0.5">
                  <Mail size={14} className="shrink-0" />
                  <span>{user.email}</span>
                </p>
              </div>

              {/* Badges */}
              <div className="flex items-center justify-center sm:justify-end gap-2 flex-wrap">
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-500/20 text-amber-950 dark:text-amber-300 border border-amber-500/30">
                  <ShieldCheck size={14} className="text-amber-700 dark:text-amber-400" />
                  <span>{roleLabel}</span>
                </span>
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-800 dark:text-emerald-300 border border-emerald-500/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                  <span>{t("profile.status_active")}</span>
                </span>
              </div>
            </div>

            <p className="text-xs text-gray-600 dark:text-gray-400 max-w-xl">
              {t("profile.welcome_description", {
                role: roleLabel,
              })}
            </p>
          </div>
        </div>
      </section>

      {/* Tabs Navigation */}
      <div className="flex items-center gap-2 border-b border-gray-200 dark:border-stone-800 overflow-x-auto no-scrollbar">
        <button
          type="button"
          onClick={() => setActiveTab("overview")}
          className={`px-4 py-2.5 text-xs sm:text-sm font-semibold rounded-t-xl transition-all whitespace-nowrap flex items-center gap-2 border-b-2 ${
            activeTab === "overview"
              ? "border-amber-600 text-amber-800 dark:text-amber-300 bg-amber-500/10 font-bold"
              : "border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          }`}
        >
          <UserIcon size={16} />
          <span>{t("profile.tab_overview")}</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("details")}
          className={`px-4 py-2.5 text-xs sm:text-sm font-semibold rounded-t-xl transition-all whitespace-nowrap flex items-center gap-2 border-b-2 ${
            activeTab === "details"
              ? "border-amber-600 text-amber-800 dark:text-amber-300 bg-amber-500/10 font-bold"
              : "border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          }`}
        >
          <Sparkles size={16} />
          <span>{t("profile.tab_edit_details")}</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("security")}
          className={`px-4 py-2.5 text-xs sm:text-sm font-semibold rounded-t-xl transition-all whitespace-nowrap flex items-center gap-2 border-b-2 ${
            activeTab === "security"
              ? "border-amber-600 text-amber-800 dark:text-amber-300 bg-amber-500/10 font-bold"
              : "border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          }`}
        >
          <KeyRound size={16} />
          <span>{t("profile.tab_security")}</span>
        </button>
      </div>

      {/* Tab 1: Overview */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Quick Shortcuts & Access */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {hasPermission("analytics:read") && (
              <Link
                to="/admin"
                className="sf-glass-card p-5 space-y-2 hover:border-amber-500/60 transition-all group"
              >
                <div className="flex items-center justify-between">
                  <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/40 text-amber-900 dark:text-amber-300 flex items-center justify-center font-bold">
                    <LayoutDashboard size={20} />
                  </div>
                  <ArrowRight
                    size={16}
                    className="text-gray-400 group-hover:text-amber-600 group-hover:translate-x-0.5 transition-all"
                  />
                </div>
                <h3 className="text-sm font-bold text-gray-900 dark:text-white">
                  {t("admin.workspace_title")}
                </h3>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  {t("profile.shortcut_admin_desc")}
                </p>
              </Link>
            )}

            <Link
              to="/check"
              className="sf-glass-card p-5 space-y-2 hover:border-amber-500/60 transition-all group"
            >
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-900/40 text-emerald-900 dark:text-emerald-300 flex items-center justify-center font-bold">
                  <Stethoscope size={20} />
                </div>
                <ArrowRight
                  size={16}
                  className="text-gray-400 group-hover:text-amber-600 group-hover:translate-x-0.5 transition-all"
                />
              </div>
              <h3 className="text-sm font-bold text-gray-900 dark:text-white">
                {t("nav.check")}
              </h3>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                {t("profile.shortcut_check_desc")}
              </p>
            </Link>

            <Link
              to="/history"
              className="sf-glass-card p-5 space-y-2 hover:border-amber-500/60 transition-all group"
            >
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900/40 text-blue-900 dark:text-blue-300 flex items-center justify-center font-bold">
                  <Clock size={20} />
                </div>
                <ArrowRight
                  size={16}
                  className="text-gray-400 group-hover:text-amber-600 group-hover:translate-x-0.5 transition-all"
                />
              </div>
              <h3 className="text-sm font-bold text-gray-900 dark:text-white">
                {t("nav.history")}
              </h3>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                {t("profile.shortcut_history_desc")}
              </p>
            </Link>
          </div>

          {/* Account Details Card */}
          <div className="sf-glass-card p-6 space-y-4">
            <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <Shield size={18} className="text-amber-600 dark:text-amber-400" />
              <span>{t("profile.account_summary_title")}</span>
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs sm:text-sm">
              <div className="p-3.5 rounded-xl bg-stone-100/80 dark:bg-stone-900/60 border border-stone-200/80 dark:border-stone-800 space-y-1">
                <span className="text-[0.68rem] uppercase font-bold text-gray-500 dark:text-gray-400 tracking-wider">
                  {t("auth.username")}
                </span>
                <p className="font-semibold text-gray-900 dark:text-white">{user.username}</p>
              </div>

              <div className="p-3.5 rounded-xl bg-stone-100/80 dark:bg-stone-900/60 border border-stone-200/80 dark:border-stone-800 space-y-1">
                <span className="text-[0.68rem] uppercase font-bold text-gray-500 dark:text-gray-400 tracking-wider">
                  {t("auth.email")}
                </span>
                <p className="font-semibold text-gray-900 dark:text-white">{user.email}</p>
              </div>

              <div className="p-3.5 rounded-xl bg-stone-100/80 dark:bg-stone-900/60 border border-stone-200/80 dark:border-stone-800 space-y-1">
                <span className="text-[0.68rem] uppercase font-bold text-gray-500 dark:text-gray-400 tracking-wider">
                  {t("profile.assigned_role")}
                </span>
                <p className="font-semibold text-gray-900 dark:text-white">{roleLabel}</p>
              </div>

              <div className="p-3.5 rounded-xl bg-stone-100/80 dark:bg-stone-900/60 border border-stone-200/80 dark:border-stone-800 space-y-1">
                <span className="text-[0.68rem] uppercase font-bold text-gray-500 dark:text-gray-400 tracking-wider">
                  {t("profile.user_id")}
                </span>
                <p className="font-mono font-semibold text-gray-900 dark:text-white">#{user.id}</p>
              </div>
            </div>
          </div>

          {/* Permissions / Capabilities */}
          {user.permissions && user.permissions.length > 0 && (
            <div className="sf-glass-card p-6 space-y-3">
              <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <Layers size={18} className="text-amber-600 dark:text-amber-400" />
                <span>{t("profile.granted_permissions_title")}</span>
              </h2>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                {t("profile.granted_permissions_desc")}
              </p>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {user.permissions.map((perm) => (
                  <span
                    key={perm}
                    className="font-mono text-[0.7rem] px-2.5 py-1 rounded-lg bg-stone-100 dark:bg-stone-900/80 border border-stone-200 dark:border-stone-800 text-stone-800 dark:text-stone-300 font-semibold"
                  >
                    {perm}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Edit Details */}
      {activeTab === "details" && (
        <div className="sf-glass-card p-6 sm:p-8 space-y-6">
          <div>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
              {t("profile.edit_details_title")}
            </h2>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
              {t("profile.edit_details_subtitle")}
            </p>
          </div>

          {detailsSuccess && (
            <div
              className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-800 dark:text-emerald-300 text-xs font-semibold flex items-center gap-2"
              role="status"
            >
              <CheckCircle2 size={16} className="shrink-0" />
              <span>{detailsSuccess}</span>
            </div>
          )}

          {detailsError && (
            <div
              className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-800 dark:text-rose-300 text-xs font-semibold flex items-center gap-2"
              role="alert"
            >
              <AlertCircle size={16} className="shrink-0" />
              <span>{detailsError}</span>
            </div>
          )}

          <form onSubmit={handleDetailsSubmit} className="space-y-4 max-w-lg">
            {/* Username Input */}
            <div className="space-y-1">
              <label
                htmlFor="profile-username"
                className="block text-xs font-bold uppercase tracking-wider text-gray-700 dark:text-gray-300"
              >
                {t("auth.username")}
              </label>
              <div className="relative">
                <UserIcon
                  size={16}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
                />
                <input
                  id="profile-username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] text-gray-900 dark:text-white focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all"
                  required
                  minLength={3}
                  maxLength={64}
                />
              </div>
            </div>

            {/* Email Input */}
            <div className="space-y-1">
              <label
                htmlFor="profile-email"
                className="block text-xs font-bold uppercase tracking-wider text-gray-700 dark:text-gray-300"
              >
                {t("auth.email")}
              </label>
              <div className="relative">
                <Mail
                  size={16}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
                />
                <input
                  id="profile-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] text-gray-900 dark:text-white focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all"
                  required
                />
              </div>
            </div>

            {/* Current Password Verification */}
            <div className="space-y-1 pt-2">
              <label
                htmlFor="details-current-password"
                className="block text-xs font-bold uppercase tracking-wider text-gray-700 dark:text-gray-300"
              >
                {t("profile.current_password_label")} <span className="text-amber-600">*</span>
              </label>
              <div className="relative">
                <KeyRound
                  size={16}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
                />
                <input
                  id="details-current-password"
                  type="password"
                  value={detailsCurrentPassword}
                  onChange={(e) => setDetailsCurrentPassword(e.target.value)}
                  placeholder={t("profile.current_password_placeholder")}
                  className="w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] text-gray-900 dark:text-white focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all placeholder:text-gray-400"
                  required
                />
              </div>
              <p className="text-[0.7rem] text-gray-500 dark:text-gray-400">
                {t("profile.password_required_hint")}
              </p>
            </div>

            <button
              type="submit"
              disabled={isDetailsSaving}
              className="sf-btn sf-btn--primary px-5 py-2.5 text-xs sm:text-sm font-bold flex items-center gap-2 disabled:opacity-50"
            >
              {isDetailsSaving && <Loader2 size={16} className="animate-spin" />}
              <span>{isDetailsSaving ? t("common.saving") : t("common.save")}</span>
            </button>
          </form>
        </div>
      )}

      {/* Tab 3: Security / Change Password */}
      {activeTab === "security" && (
        <div className="sf-glass-card p-6 sm:p-8 space-y-6">
          <div>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
              {t("profile.change_password_title")}
            </h2>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
              {t("profile.change_password_subtitle")}
            </p>
          </div>

          {passwordSuccess && (
            <div
              className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-800 dark:text-emerald-300 text-xs font-semibold flex items-center gap-2"
              role="status"
            >
              <CheckCircle2 size={16} className="shrink-0" />
              <span>{passwordSuccess}</span>
            </div>
          )}

          {passwordError && (
            <div
              className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-800 dark:text-rose-300 text-xs font-semibold flex items-center gap-2"
              role="alert"
            >
              <AlertCircle size={16} className="shrink-0" />
              <span>{passwordError}</span>
            </div>
          )}

          <form onSubmit={handlePasswordSubmit} className="space-y-4 max-w-lg">
            {/* Current Password */}
            <div className="space-y-1">
              <label
                htmlFor="sec-current-password"
                className="block text-xs font-bold uppercase tracking-wider text-gray-700 dark:text-gray-300"
              >
                {t("profile.current_password_label")}
              </label>
              <div className="relative">
                <KeyRound
                  size={16}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
                />
                <input
                  id="sec-current-password"
                  type={showCurrentPass ? "text" : "password"}
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2.5 text-sm rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] text-gray-900 dark:text-white focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowCurrentPass(!showCurrentPass)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                  aria-label={showCurrentPass ? "Hide input text" : "Show input text"}
                >
                  {showCurrentPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {/* New Password */}
            <div className="space-y-1">
              <label
                htmlFor="sec-new-password"
                className="block text-xs font-bold uppercase tracking-wider text-gray-700 dark:text-gray-300"
              >
                {t("profile.new_password_label")}
              </label>
              <div className="relative">
                <KeyRound
                  size={16}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
                />
                <input
                  id="sec-new-password"
                  type={showNewPass ? "text" : "password"}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2.5 text-sm rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] text-gray-900 dark:text-white focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all"
                  required
                  minLength={8}
                  maxLength={128}
                />
                <button
                  type="button"
                  onClick={() => setShowNewPass(!showNewPass)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                  aria-label={showNewPass ? "Hide input text" : "Show input text"}
                >
                  {showNewPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              <p className="text-[0.7rem] text-gray-500 dark:text-gray-400">
                {t("auth.password_help")}
              </p>
            </div>

            {/* Confirm New Password */}
            <div className="space-y-1">
              <label
                htmlFor="sec-confirm-password"
                className="block text-xs font-bold uppercase tracking-wider text-gray-700 dark:text-gray-300"
              >
                {t("profile.confirm_new_password_label")}
              </label>
              <div className="relative">
                <KeyRound
                  size={16}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
                />
                <input
                  id="sec-confirm-password"
                  type={showNewPass ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2.5 text-sm rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] text-gray-900 dark:text-white focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all"
                  required
                  minLength={8}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isPasswordSaving}
              className="sf-btn sf-btn--primary px-5 py-2.5 text-xs sm:text-sm font-bold flex items-center gap-2 disabled:opacity-50"
            >
              {isPasswordSaving && <Loader2 size={16} className="animate-spin" />}
              <span>{isPasswordSaving ? t("common.saving") : t("profile.change_password_button")}</span>
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
