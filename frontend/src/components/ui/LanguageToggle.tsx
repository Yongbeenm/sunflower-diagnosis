import type React from "react";
import { useTranslation } from "react-i18next";

/**
 * EN/KM language toggle button.
 * Switches the i18next locale and mirrors it onto <html lang="...">.
 */
export function LanguageToggle(): React.JSX.Element {
  const { i18n } = useTranslation();

  const isKhmer = i18n.language === "km";

  const toggle = () => {
    void i18n.changeLanguage(isKhmer ? "en" : "km");
  };

  return (
    <button
      type="button"
      className="sf-lang-toggle"
      onClick={toggle}
      aria-label={isKhmer ? "Switch to English" : "ប្ដូរទៅភាសាខ្មែរ"}
      title={isKhmer ? "Switch to English" : "ប្ដូរទៅភាសាខ្មែរ"}
    >
      <span className="sf-lang-toggle__flag" aria-hidden="true">
        {isKhmer ? "🇬🇧" : "🇰🇭"}
      </span>
      <span className="sf-lang-toggle__label">{isKhmer ? "EN" : "ខ្មែរ"}</span>
    </button>
  );
}
