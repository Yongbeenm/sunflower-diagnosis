import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router";
import { UserPlus, User, Mail, Lock, Eye, EyeOff, AlertCircle, Loader2 } from "lucide-react";
import { useAuth } from "../context";
import { registerSchema, type RegisterFormData } from "../schemas";

export function RegisterPage(): React.JSX.Element {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { register: registerUser } = useAuth();
  const [serverError, setServerError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: "",
      username: "",
      password: "",
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setServerError(null);
      await registerUser(data);
      navigate("/");
    } catch (err: unknown) {
      const errorMsg =
        err instanceof Error && err.message ? err.message : t("auth.register_failed");
      setServerError(errorMsg);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-10 px-4">
      <div className="sf-glass-card max-w-md w-full p-6 sm:p-8 space-y-6 shadow-xl border border-[var(--color-border)] dark:border-[var(--color-border)] relative overflow-hidden">
        {/* Subtle glowing ambient aura */}
        <div
          className="absolute -top-16 left-1/2 -translate-x-1/2 w-56 h-56 rounded-full bg-amber-400/15 dark:bg-amber-400/10 blur-2xl pointer-events-none"
          aria-hidden="true"
        />

        <div className="text-center space-y-2 relative">
          <div className="w-14 h-14 rounded-2xl bg-amber-500/15 dark:bg-amber-400/15 text-amber-600 dark:text-amber-400 flex items-center justify-center mx-auto text-2xl shadow-inner border border-amber-500/25">
            🌻
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-[var(--color-text)] dark:text-[var(--color-text)]">
            {t("auth.register_title")}
          </h1>
          <p className="text-xs sm:text-sm text-[var(--color-text-muted)] dark:text-[var(--color-text-muted)]">
            {t("auth.register_subtitle")}
          </p>
        </div>

        {serverError && (
          <div
            role="alert"
            className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900 flex items-start gap-2.5 text-xs text-rose-700 dark:text-rose-300 font-medium animate-in fade-in duration-200"
          >
            <AlertCircle size={16} className="shrink-0 text-rose-500 mt-0.5" />
            <span>{serverError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
          <div className="space-y-1.5">
            <label
              htmlFor="email"
              className="block text-xs font-bold uppercase tracking-wider text-[var(--color-text-secondary)] dark:text-[var(--color-text-secondary)]"
            >
              {t("auth.email_label")}
            </label>
            <div className="relative">
              <Mail
                size={16}
                className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"
              />
              <input
                id="email"
                type="email"
                autoComplete="email"
                placeholder={t("auth.email_placeholder")}
                {...register("email")}
                className="w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl bg-[var(--color-surface)] dark:bg-[var(--color-surface)] border border-[var(--color-border)] dark:border-[var(--color-border)] focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all"
              />
            </div>
            {errors.email?.message && (
              <p role="alert" className="text-xs text-rose-500 font-medium pt-0.5">
                {t(errors.email.message)}
              </p>
            )}
          </div>

          <div className="space-y-1.5">
            <label
              htmlFor="username"
              className="block text-xs font-bold uppercase tracking-wider text-[var(--color-text-secondary)] dark:text-[var(--color-text-secondary)]"
            >
              {t("auth.username_label")}
            </label>
            <div className="relative">
              <User
                size={16}
                className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"
              />
              <input
                id="username"
                type="text"
                autoComplete="username"
                placeholder={t("auth.username_placeholder")}
                {...register("username")}
                className="w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl bg-[var(--color-surface)] dark:bg-[var(--color-surface)] border border-[var(--color-border)] dark:border-[var(--color-border)] focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all"
              />
            </div>
            {errors.username?.message && (
              <p role="alert" className="text-xs text-rose-500 font-medium pt-0.5">
                {t(errors.username.message)}
              </p>
            )}
          </div>

          <div className="space-y-1.5">
            <label
              htmlFor="password"
              className="block text-xs font-bold uppercase tracking-wider text-[var(--color-text-secondary)] dark:text-[var(--color-text-secondary)]"
            >
              {t("auth.password_label")}
            </label>
            <div className="relative">
              <Lock
                size={16}
                className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"
              />
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                placeholder={t("auth.password_placeholder")}
                {...register("password")}
                className="w-full pl-10 pr-10 py-2.5 text-sm rounded-xl bg-[var(--color-surface)] dark:bg-[var(--color-surface)] border border-[var(--color-border)] dark:border-[var(--color-border)] focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-[var(--color-text-muted)] dark:hover:text-[var(--color-text)]"
                aria-label={showPassword ? "Hide input text" : "Show input text"}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.password?.message && (
              <p role="alert" className="text-xs text-rose-500 font-medium pt-0.5">
                {t(errors.password.message)}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-2.5 px-4 rounded-xl font-bold text-sm bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 mt-2"
          >
            {isSubmitting ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <UserPlus size={16} />
            )}
            <span>{isSubmitting ? t("common.loading") : t("auth.sign_up_btn")}</span>
          </button>
        </form>

        <p className="text-center text-xs text-[var(--color-text-muted)] dark:text-[var(--color-text-muted)] pt-2 border-t border-slate-100 dark:border-slate-800">
          {t("auth.already_have_account")}{" "}
          <Link
            to="/login"
            className="text-amber-600 dark:text-amber-400 font-bold hover:underline"
          >
            {t("auth.login_link")}
          </Link>
        </p>
      </div>
    </div>
  );
}
