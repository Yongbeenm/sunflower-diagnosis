import type React from "react";
import { Link, useLocation, Outlet, Navigate } from "react-router";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart3,
  Microscope,
  Leaf,
  MessageSquare,
  Users,
  ShieldCheck,
  ArrowLeft,
} from "lucide-react";
import { useAuth } from "@/features/auth";
import { apiFetch } from "@/api/client";
import { LanguageToggle } from "@/components/ui/LanguageToggle";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { ThemeBackground } from "@/components/layout/ThemeBackground";

interface SystemStats {
  total_diseases: number;
  total_symptoms: number;
  published_diseases: number;
}

interface AdminNavItem {
  to: string;
  labelKey: string;
  icon: typeof BarChart3;
  permission: string;
  exact?: boolean;
  statKey?: "total_diseases" | "total_symptoms";
}

const ADMIN_NAV_ITEMS: AdminNavItem[] = [
  {
    to: "/admin",
    labelKey: "admin.nav_overview",
    icon: BarChart3,
    permission: "analytics:read",
    exact: true,
  },
  {
    to: "/admin/diseases",
    labelKey: "admin.nav_diseases",
    icon: Microscope,
    permission: "disease:read",
    statKey: "total_diseases",
  },
  {
    to: "/admin/symptoms",
    labelKey: "admin.nav_symptoms",
    icon: Leaf,
    permission: "symptom:read",
    statKey: "total_symptoms",
  },
  {
    to: "/admin/feedback",
    labelKey: "admin.nav_feedback",
    icon: MessageSquare,
    permission: "feedback:read",
  },
  {
    to: "/admin/users",
    labelKey: "admin.nav_users",
    icon: Users,
    permission: "user:manage",
  },
  {
    to: "/admin/roles",
    labelKey: "admin.nav_roles",
    icon: ShieldCheck,
    permission: "rbac:manage",
  },
];

export function AdminLayout(): React.JSX.Element {
  const { t } = useTranslation();
  const { user, isAuthenticated, isLoading, hasPermission } = useAuth();
  const location = useLocation();

  const { data: stats } = useQuery({
    queryKey: ["system-stats"],
    queryFn: () => apiFetch<SystemStats>("/public/stats"),
    staleTime: 30_000,
  });

  if (isLoading && !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg)]" aria-busy="true">
        <div className="sf-spinner" aria-label="Loading admin portal..." />
      </div>
    );
  }

  if (!isAuthenticated && !user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  // Filter navigation items: Admins have full access; experts/agronomists require specific permissions
  const allowedItems = ADMIN_NAV_ITEMS.filter(
    (item) => user?.role === "admin" || hasPermission(item.permission),
  );

  // If user has zero admin/agronomy permissions, redirect to grower portal
  if (!isLoading && user && user.role !== "admin" && allowedItems.length === 0) {
    return <Navigate to="/" replace />;
  }

  const isActive = (item: AdminNavItem) => {
    if (item.exact) {
      return location.pathname === item.to;
    }
    return location.pathname.startsWith(item.to);
  };

  return (
    <div className="min-h-screen flex flex-col relative text-[var(--color-text)]">
      {/* Responsive Theme-Aware Fixed Sunflower Background */}
      <ThemeBackground />

      {/* Top Admin Header */}
      <header className="sticky top-0 z-40 bg-white/85 dark:bg-[#202917]/85 backdrop-blur-md border-b border-stone-200/80 dark:border-white/10">
        <div className="max-w-7xl mx-auto px-3 sm:px-6 h-16 flex items-center justify-between gap-2 sm:gap-4">
          <div className="flex items-center gap-2 sm:gap-3 min-w-0">
            <Link to="/admin" className="flex items-center gap-2 sm:gap-2.5 text-decoration-none group min-w-0">
              <span className="text-2xl transition-transform group-hover:scale-110 shrink-0" aria-hidden="true">
                🌻
              </span>
              <div className="flex flex-col min-w-0">
                <span className="font-bold text-sm sm:text-base tracking-tight text-gray-900 dark:text-white leading-tight truncate">
                  {t("admin.workspace_title")}
                </span>
                <span className="text-[0.62rem] sm:text-[0.65rem] font-bold text-amber-700 dark:text-amber-400 tracking-wider uppercase font-mono truncate">
                  {user?.role === "admin" ? "Administrator Workspace" : "Agronomist Portal"}
                </span>
              </div>
            </Link>

            {user?.role && (
              <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[0.68rem] font-bold uppercase tracking-wider bg-amber-500/15 text-amber-900 dark:text-amber-200 border border-amber-500/30 shrink-0">
                <ShieldCheck size={12} className="text-amber-600 dark:text-amber-400" />
                <span>{user.role === "admin" ? "Admin" : user.role === "expert" ? "Expert" : user.role}</span>
              </span>
            )}
          </div>

          <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
            <Link
              to="/"
              className="sf-btn sf-btn--ghost sf-btn--sm text-xs flex items-center gap-1.5 font-semibold text-gray-700 dark:text-gray-200 hover:text-gray-900 dark:hover:text-white whitespace-nowrap"
            >
              <ArrowLeft size={14} className="shrink-0" />
              <span className="hidden sm:inline">{t("admin.back_to_grower_app")}</span>
              <span className="sm:hidden">App</span>
            </Link>

            <ThemeToggle />
            <LanguageToggle />
          </div>
        </div>
      </header>

      {/* Body: Sidebar + Main Content */}
      <div className="flex-1 max-w-7xl w-full mx-auto flex flex-col md:flex-row min-h-0">
        {/* Sidebar */}
        <aside
          className="w-full md:w-60 shrink-0 border-b md:border-b-0 md:border-r border-stone-200/80 dark:border-white/10 p-3 sm:p-4 bg-white/70 dark:bg-[#202917]/75 backdrop-blur-md"
          aria-label={t("admin.sidebar_label")}
        >
          <nav className="flex md:flex-col gap-1.5 overflow-x-auto pb-1 md:pb-0 no-scrollbar">
            {allowedItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item);
              const count = item.statKey ? (stats?.[item.statKey] ?? (item.statKey === "total_diseases" ? 5 : 20)) : null;

              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`px-3 py-2.5 rounded-xl text-xs font-semibold flex items-center gap-2.5 transition-all whitespace-nowrap shrink-0 md:shrink ${
                    active
                      ? "bg-amber-500/20 text-amber-950 dark:text-amber-200 border border-amber-500/40 shadow-xs font-bold"
                      : "text-gray-700 dark:text-gray-200 hover:bg-amber-500/10 dark:hover:bg-white/5 hover:text-gray-900 dark:hover:text-white border border-transparent"
                  }`}
                >
                  <Icon size={16} className={`shrink-0 ${active ? "text-amber-600 dark:text-amber-400" : "text-gray-500 dark:text-gray-400"}`} />
                  <span className="truncate flex-1">{t(item.labelKey)}</span>
                  {count !== null && (
                    <span
                      className={`px-1.5 py-0.5 rounded-md text-[0.65rem] font-mono font-bold shrink-0 ${
                        active
                          ? "bg-amber-500/30 text-amber-950 dark:text-amber-100"
                          : "bg-stone-200/80 dark:bg-white/10 text-gray-700 dark:text-gray-300"
                      }`}
                    >
                      {count}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </aside>

        {/* Workspace Content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

