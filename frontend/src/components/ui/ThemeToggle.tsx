import type React from "react";
import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";

export function ThemeToggle(): React.JSX.Element {
  const [isDark, setIsDark] = useState<boolean>(() => {
    if (typeof window === "undefined") return false;
    const stored = localStorage.getItem("sf-theme");
    if (stored) return stored === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.setAttribute("data-theme", "dark");
      localStorage.setItem("sf-theme", "dark");
    } else {
      root.setAttribute("data-theme", "light");
      localStorage.setItem("sf-theme", "light");
    }
  }, [isDark]);

  return (
    <button
      type="button"
      onClick={() => setIsDark((prev) => !prev)}
      className="sf-btn sf-btn--ghost sf-btn--sm"
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "0.4rem 0.6rem",
        borderRadius: "var(--radius-md)",
      }}
      aria-label={isDark ? "Switch to light theme" : "Switch to dark theme"}
      title={isDark ? "Switch to light theme" : "Switch to dark theme"}
    >
      {isDark ? (
        <Sun size={18} className="text-amber-400" aria-hidden="true" />
      ) : (
        <Moon size={18} className="text-slate-600" aria-hidden="true" />
      )}
    </button>
  );
}
