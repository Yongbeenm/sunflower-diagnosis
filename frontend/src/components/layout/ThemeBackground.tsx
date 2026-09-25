import type React from "react";
import lightBg from "@/assets/images/sunflower-website-background-lightMode.jpg";
import darkBg from "@/assets/images/sunflower-website-background-darkMode.jpeg";

/**
 * ThemeBackground Component
 *
 * Implements a responsive, theme-aware, fixed background image that smoothly
 * crossfades between light and dark mode sunflower photographs with optimized
 * contrast tint overlays for crystal-clear text readability.
 */
export function ThemeBackground(): React.JSX.Element {
  return (
    <div
      className="fixed inset-0 pointer-events-none -z-50 overflow-hidden select-none"
      aria-hidden="true"
    >
      {/* Light Mode Sunflower Background */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat bg-fixed transition-opacity duration-700 ease-in-out opacity-100 dark:opacity-0 will-change-[opacity]"
        style={{ backgroundImage: `url(${lightBg})` }}
      />

      {/* Dark Mode Sunflower Background */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat bg-fixed transition-opacity duration-700 ease-in-out opacity-0 dark:opacity-100 will-change-[opacity]"
        style={{ backgroundImage: `url(${darkBg})` }}
      />

      {/* Enhanced Frosted Glass Readability Overlay with Richer Blur:
          - backdrop-blur-[12px] (or backdrop-blur-md) provides a beautiful, soft bokeh/frosted aesthetic.
          - Balances light and dark mode tones for crystal-clear readability. */}
      <div className="absolute inset-0 bg-white/55 dark:bg-[#0B1006]/70 backdrop-blur-[12px] transition-colors duration-700 ease-in-out" />
    </div>
  );
}
