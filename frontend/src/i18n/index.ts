/**
 * i18next initialisation.
 *
 * - Loads en and km resources from src/locales/.
 * - Detects and persists the active locale in localStorage ("i18nextLng").
 * - Mirrors the active locale onto document.documentElement.lang so that
 *   :lang(km) CSS rules and browser accessibility tools work correctly.
 *
 * Import this module as a side-effect in main.tsx:
 *   import "@/i18n/index";
 */

import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import en from "@/locales/en.json";
import km from "@/locales/km.json";

const SUPPORTED_LOCALES = ["en", "km"] as const;
export type Locale = (typeof SUPPORTED_LOCALES)[number];

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      km: { translation: km },
    },
    supportedLngs: [...SUPPORTED_LOCALES],
    fallbackLng: "en",
    interpolation: {
      escapeValue: false, // React already escapes
    },
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
      lookupLocalStorage: "i18nextLng",
    },
  });

/** Mirror the active locale onto <html lang="…"> so CSS :lang() rules apply. */
function syncHtmlLang(lng: string): void {
  document.documentElement.lang = lng;
}

// Sync once on startup.
syncHtmlLang(i18n.language);

// Keep in sync as the user switches languages.
i18n.on("languageChanged", syncHtmlLang);

export default i18n;
