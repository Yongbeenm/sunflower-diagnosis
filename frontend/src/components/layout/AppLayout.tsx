import type React from "react";
import { useState } from "react";
import { Link, useLocation } from "react-router";
import { useTranslation } from "react-i18next";
import {
  Home,
  BookOpen,
  Stethoscope,
  Clock,
  Info,
  LogOut,
  LogIn,
  LayoutDashboard,
} from "lucide-react";
import { useAuth } from "@/features/auth";
import { LanguageToggle } from "@/components/ui/LanguageToggle";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { AboutModal } from "./AboutModal";
import { BottomNav } from "./BottomNav";
import { AIChatWidget } from "@/features/ai-assistant";
import { ThemeBackground } from "./ThemeBackground";
import { OfflineBanner } from "@/components/ui/OfflineBanner";

interface NavItem {
  to: string;
  labelKey: string;
  icon: typeof Home;
  requireAuth?: boolean;
  requirePermission?: string; // Any permission from a list
}

const NAV_ITEMS: NavItem[] = [
  { to: "/", labelKey: "nav.home", icon: Home },
  { to: "/check", labelKey: "nav.check", icon: Stethoscope },
  { to: "/diseases", labelKey: "nav.diseases", icon: BookOpen },
  { to: "/history", labelKey: "nav.history", icon: Clock, requireAuth: true },
  {
    to: "/admin",
    labelKey: "nav.dashboard", // Will show "Admin" or "Expert" based on role
    icon: LayoutDashboard,
    requireAuth: true,
    requirePermission: "analytics:read", // Any admin/expert permission
  },
];

/**
 * Main application layout with frosted glass header and mobile floating dock.
 */
export function AppLayout({ children }: { children: React.ReactNode }): React.JSX.Element {
  const { t } = useTranslation();
  const { isAuthenticated, logout, user, hasPermission } = useAuth();
  const location = useLocation();
  const [isAboutOpen, setIsAboutOpen] = useState(false);

  const isActive = (path: string) => {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  };

  const visibleNav = NAV_ITEMS.filter((item) => {
    // Check authentication requirement
    if (item.requireAuth && !isAuthenticated) return false;

    // Check permission requirement
    if (item.requirePermission && !hasPermission(item.requirePermission)) return false;

    return true;
  });

  return (
    <div className="sf-layout min-h-screen flex flex-col relative text-[var(--color-text)]">
      {/* Responsive Theme-Aware Fixed Sunflower Background */}
      <ThemeBackground />

      {/* About Expert System Modal */}
      <AboutModal isOpen={isAboutOpen} onClose={() => setIsAboutOpen(false)} />

      {/* AI Chat Widget - Shows for authenticated users */}
      <AIChatWidget />

      {/* Desktop Header */}
      <header className="sticky top-0 z-40 bg-white/85 dark:bg-[#202917]/85 backdrop-blur-md border-b border-stone-200/80 dark:border-white/10 transition-colors">
        <div className="max-w-6xl mx-auto px-3 sm:px-6 h-16 flex items-center justify-between gap-2 sm:gap-4">
          {/* Brand */}
          <Link
            to="/"
            className="flex items-center gap-2 text-decoration-none shrink min-w-0 group"
          >
            <span
              className="text-2xl transition-transform group-hover:scale-110 shrink-0"
              aria-hidden="true"
            >
              🌻
            </span>
            <div className="flex flex-col min-w-0">
              <span className="font-bold text-sm sm:text-base tracking-tight text-gray-900 dark:text-white leading-tight truncate">
                {t("app.title")}
              </span>
              <span className="text-[0.62rem] sm:text-[0.65rem] font-bold text-amber-900 dark:text-amber-400 tracking-wider uppercase font-mono truncate">
                AI Expert System
              </span>
            </div>
          </Link>

          {/* Desktop Navigation - active on lg screens where all text fits without overflow */}
          <nav className="hidden lg:flex items-center gap-1 shrink-0" aria-label="Main navigation">
            {visibleNav.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.to);

              // Show "Admin" for admin role, "Expert" for expert role
              let label = t(item.labelKey);
              if (item.to === "/admin" && user) {
                label = user.role === "admin" ? t("nav.admin") : t("nav.expert");
              }

              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`px-2.5 xl:px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all whitespace-nowrap ${
                    active
                      ? "bg-amber-500/20 text-amber-950 dark:text-amber-200 border border-amber-500/40 shadow-xs font-bold"
                      : "text-gray-700 dark:text-gray-200 hover:bg-amber-500/10 dark:hover:bg-white/5 hover:text-gray-900 dark:hover:text-white"
                  }`}
                >
                  <Icon size={15} className="shrink-0" />
                  <span>{label}</span>
                </Link>
              );
            })}

            {/* About Modal Trigger */}
            <button
              type="button"
              onClick={() => setIsAboutOpen(true)}
              className="px-2.5 xl:px-3 py-1.5 rounded-xl text-xs font-semibold text-gray-700 dark:text-gray-200 hover:bg-amber-500/10 dark:hover:bg-white/5 hover:text-gray-900 dark:hover:text-white flex items-center gap-1.5 transition-all whitespace-nowrap"
            >
              <Info size={15} className="shrink-0" />
              <span>{t("nav.about")}</span>
            </button>
          </nav>

          {/* Right Controls: Theme + Language + Auth */}
          <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
            <ThemeToggle />
            <LanguageToggle />

            {isAuthenticated ? (
              <div className="flex items-center gap-1.5 sm:gap-2 pl-1 sm:pl-2 border-l border-gray-200 dark:border-white/10 shrink-0">
                <Link
                  to="/profile"
                  className="flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-semibold text-gray-700 dark:text-gray-200 hover:bg-stone-100 dark:hover:bg-white/5 hover:text-amber-800 dark:hover:text-amber-300 transition-all max-w-[140px]"
                  title={t("nav.profile")}
                >
                  <div className="w-5 h-5 rounded-full bg-amber-500/20 text-amber-950 dark:text-amber-300 flex items-center justify-center font-bold text-[0.65rem] uppercase shrink-0 border border-amber-500/30">
                    {user?.username?.slice(0, 1)}
                  </div>
                  <span className="hidden sm:inline truncate">{user?.username}</span>
                </Link>
                <button
                  type="button"
                  onClick={() => void logout()}
                  className="sf-btn sf-btn--ghost sf-btn--sm text-xs flex items-center gap-1 text-gray-600 hover:text-rose-600 dark:text-gray-300 dark:hover:text-rose-400 whitespace-nowrap"
                  title={t("nav.logout")}
                  aria-label={t("nav.logout")}
                >
                  <LogOut size={14} className="shrink-0" />
                  <span className="hidden sm:inline">{t("nav.logout")}</span>
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="sf-btn sf-btn--primary sf-btn--sm text-xs flex items-center gap-1 whitespace-nowrap shrink-0"
              >
                <LogIn size={14} className="shrink-0" />
                <span>{t("nav.login")}</span>
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Offline Status & Sync Banner */}
      <OfflineBanner />

      {/* Main Content Viewport */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-6 pb-24 md:pb-12">
        {children}
      </main>

      {/* Mobile Floating Bottom Dock */}
      <BottomNav onOpenAbout={() => setIsAboutOpen(true)} />
    </div>
  );
}
