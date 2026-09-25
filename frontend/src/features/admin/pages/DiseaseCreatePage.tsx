import type React from "react";
import { useState } from "react";
import { useNavigate, Link } from "react-router";
import { useTranslation } from "react-i18next";
import {
  ArrowLeft,
  Sparkles,
  Languages,
  FileText,
  ShieldAlert,
  Pill,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  ShieldCheck,
  AlertCircle,
} from "lucide-react";
import { useCreateDisease } from "../hooks";

export function DiseaseCreatePage(): React.JSX.Element {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const createMutation = useCreateDisease();

  const [slug, setSlug] = useState("");
  const [pathogenType, setPathogenType] = useState("fungal");
  const [isPublished, setIsPublished] = useState(false);
  
  // English content
  const [nameEn, setNameEn] = useState("");
  const [descriptionEn, setDescriptionEn] = useState("");
  const [causeEn, setCauseEn] = useState("");
  const [treatmentEn, setTreatmentEn] = useState("");
  const [preventionEn, setPreventionEn] = useState("");
  
  // Khmer content
  const [nameKm, setNameKm] = useState("");
  const [descriptionKm, setDescriptionKm] = useState("");
  const [causeKm, setCauseKm] = useState("");
  const [treatmentKm, setTreatmentKm] = useState("");
  const [preventionKm, setPreventionKm] = useState("");

  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleNameEnChange = (val: string) => {
    setNameEn(val);
    if (!slug) {
      // Auto-generate slug from English name
      setSlug(
        val
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/(^-|-$)/g, ""),
      );
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nameEn.trim() || !slug.trim()) return;

    setErrorMessage(null);
    try {
      const created = await createMutation.mutateAsync({
        slug: slug.trim(),
        pathogen_type: pathogenType,
        is_published: isPublished,
        name_en: nameEn.trim(),
        description_en: descriptionEn.trim() || undefined,
        cause_en: causeEn.trim() || undefined,
        treatment_en: treatmentEn.trim() || undefined,
        prevention_en: preventionEn.trim() || undefined,
        name_km: nameKm.trim() || undefined,
        description_km: descriptionKm.trim() || undefined,
        cause_km: causeKm.trim() || undefined,
        treatment_km: treatmentKm.trim() || undefined,
        prevention_km: preventionKm.trim() || undefined,
      });

      // Redirect to disease list after creation
      void navigate(`/admin/diseases/${created.slug}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : t("common.error");
      setErrorMessage(msg);
    }
  };

  // Calculate translation completeness
  const kmFields = [nameKm, descriptionKm, causeKm, treatmentKm, preventionKm];
  const translatedCount = kmFields.filter((f) => !!f.trim()).length;
  const completenessPercent = Math.round((translatedCount / 5) * 100);

  return (
    <div className="max-w-4xl mx-auto px-4 py-2 pb-12">
      {/* Header */}
      <div className="mb-6">
        <Link
          to="/admin/diseases"
          className="sf-btn sf-btn--ghost sf-btn--sm inline-flex items-center gap-1.5 text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text)] mb-3 px-2 py-1 rounded-lg"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>{t("admin.back_to_diseases")}</span>
        </Link>
        <h1 className="sf-section-title text-2xl font-bold tracking-tight">
          {t("admin.create_disease_title")}
        </h1>
        <p className="sf-section-subtitle text-sm text-[var(--color-text-muted)] mt-1">
          {t("admin.create_disease_subtitle")}
        </p>
      </div>

      <form onSubmit={(e) => void handleSubmit(e)} className="flex flex-col gap-6">
        {/* Basic Info Card */}
        <div className="sf-card p-6 shadow-sm border border-[var(--color-border)]">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-[var(--color-border-subtle)]">
            <Sparkles className="w-4 h-4 text-amber-600" />
            <h2 className="font-bold text-base text-[var(--color-text)]">Basic Information</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="sf-form__group">
              <label htmlFor="disease-name-en" className="sf-form__label text-xs font-semibold">
                🇬🇧 {t("admin.disease_name_label")} (English) *
              </label>
              <input
                id="disease-name-en"
                type="text"
                required
                className="sf-form__input text-sm rounded-xl"
                value={nameEn}
                onChange={(e) => handleNameEnChange(e.target.value)}
                placeholder="e.g. Alternaria Leaf Spot"
              />
              {slug && (
                <div className="text-[11px] text-[var(--color-text-muted)] mt-1">
                  URL slug: <code className="font-mono text-amber-600 font-semibold">{slug}</code>
                </div>
              )}
            </div>

            <div className="sf-form__group">
              <label htmlFor="disease-name-km" className="sf-form__label text-xs font-semibold">
                🇰🇭 {t("admin.disease_name_label")} (ខ្មែរ)
              </label>
              <input
                id="disease-name-km"
                type="text"
                className="sf-form__input text-sm rounded-xl font-khmer"
                value={nameKm}
                onChange={(e) => setNameKm(e.target.value)}
                placeholder="e.g. ជំងឺស្នាមត្នោតលើស្លឹក"
                lang="km"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
            <div className="sf-form__group">
              <label htmlFor="pathogen-type" className="sf-form__label text-xs font-semibold">
                {t("diseases.filter_pathogen")} *
              </label>
              <select
                id="pathogen-type"
                className="sf-filter-select w-full text-sm rounded-xl"
                value={pathogenType}
                onChange={(e) => setPathogenType(e.target.value)}
              >
                <option value="fungal">{t("diseases.pathogen_fungal")}</option>
                <option value="bacterial">{t("diseases.pathogen_bacterial")}</option>
                <option value="viral">{t("diseases.pathogen_viral")}</option>
                <option value="abiotic">{t("diseases.pathogen_abiotic")}</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div className="flex items-center gap-3 pt-6">
              <label className="relative flex items-center gap-2.5 cursor-pointer">
                <input
                  id="is-published"
                  type="checkbox"
                  checked={isPublished}
                  onChange={(e) => setIsPublished(e.target.checked)}
                  className="w-4 h-4 text-amber-600 rounded border-[var(--color-border)] focus:ring-amber-500 accent-amber-600"
                />
                <span className="text-sm font-medium text-[var(--color-text)] select-none">
                  {t("admin.publish_immediately")}
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Translation Completeness Card */}
        <div className="sf-card p-4 shadow-sm border border-[var(--color-border)] bg-[var(--color-bg-subtle)]/50">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-amber-500/10 text-amber-600 flex items-center justify-center">
                <Languages className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-[var(--color-text)]">
                  {t("admin.translation_completeness")}: {completenessPercent}%
                </h3>
                <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
                  {t("admin.fields_translated_summary", {
                    translated: translatedCount,
                    total: 5,
                  })}
                </p>
              </div>
            </div>

            <div className="w-full sm:w-48 h-2.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-500 transition-all duration-300 rounded-full"
                style={{ width: `${completenessPercent}%` }}
              />
            </div>
          </div>
        </div>

        {/* Description Field */}
        <div
          className={`sf-card p-5 shadow-sm border transition-all ${
            descriptionKm.trim()
              ? "border-amber-200 dark:border-amber-900/50"
              : "border-amber-200 dark:border-amber-900/50"
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-amber-600" />
              <h3 className="text-sm font-bold text-[var(--color-text)]">Description</h3>
            </div>
            {!descriptionKm.trim() && (
              <span className="sf-badge sf-badge--warning text-[11px] px-2 py-0.5 inline-flex items-center gap-1 font-medium rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400">
                <AlertTriangle className="w-3 h-3" />
                <span>{t("admin.missing_km_translation")}</span>
              </span>
            )}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-[var(--color-text-muted)] block mb-1">
                🇬🇧 English
              </label>
              <textarea
                className="sf-form__textarea text-sm rounded-xl w-full min-h-[5.5rem]"
                value={descriptionEn}
                onChange={(e) => setDescriptionEn(e.target.value)}
                placeholder="What does this disease look like?"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-[var(--color-text-muted)] block mb-1">
                🇰🇭 ខ្មែរ
              </label>
              <textarea
                className="sf-form__textarea text-sm rounded-xl w-full min-h-[5.5rem] font-khmer"
                value={descriptionKm}
                onChange={(e) => setDescriptionKm(e.target.value)}
                placeholder="ជំងឺនេះមើលទៅដូចម្តេច?"
                lang="km"
              />
            </div>
          </div>
        </div>

        {/* Cause Field */}
        <div
          className={`sf-card p-5 shadow-sm border transition-all ${
            causeKm.trim()
              ? "border-amber-200 dark:border-amber-900/50"
              : "border-amber-200 dark:border-amber-900/50"
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-600" />
              <h3 className="text-sm font-bold text-[var(--color-text)]">Cause</h3>
            </div>
            {!causeKm.trim() && (
              <span className="sf-badge sf-badge--warning text-[11px] px-2 py-0.5 inline-flex items-center gap-1 font-medium rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400">
                <AlertTriangle className="w-3 h-3" />
                <span>{t("admin.missing_km_translation")}</span>
              </span>
            )}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-[var(--color-text-muted)] block mb-1">
                🇬🇧 English
              </label>
              <textarea
                className="sf-form__textarea text-sm rounded-xl w-full min-h-[5.5rem]"
                value={causeEn}
                onChange={(e) => setCauseEn(e.target.value)}
                placeholder="What causes this disease? (pathogen, conditions)"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-[var(--color-text-muted)] block mb-1">
                🇰🇭 ខ្មែរ
              </label>
              <textarea
                className="sf-form__textarea text-sm rounded-xl w-full min-h-[5.5rem] font-khmer"
                value={causeKm}
                onChange={(e) => setCauseKm(e.target.value)}
                placeholder="អ្វីជាមូលហេតុនៃជំងឺនេះ?"
                lang="km"
              />
            </div>
          </div>
        </div>

        {/* Treatment Field */}
        <div
          className={`sf-card p-5 shadow-sm border transition-all ${
            treatmentKm.trim()
              ? "border-amber-200 dark:border-amber-900/50"
              : "border-amber-200 dark:border-amber-900/50"
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Pill className="w-4 h-4 text-amber-600" />
              <h3 className="text-sm font-bold text-[var(--color-text)]">Treatment</h3>
            </div>
            {!treatmentKm.trim() && (
              <span className="sf-badge sf-badge--warning text-[11px] px-2 py-0.5 inline-flex items-center gap-1 font-medium rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400">
                <AlertTriangle className="w-3 h-3" />
                <span>{t("admin.missing_km_translation")}</span>
              </span>
            )}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-[var(--color-text-muted)] block mb-1">
                🇬🇧 English
              </label>
              <textarea
                className="sf-form__textarea text-sm rounded-xl w-full min-h-[5.5rem]"
                value={treatmentEn}
                onChange={(e) => setTreatmentEn(e.target.value)}
                placeholder="How to treat this disease once infected?"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-[var(--color-text-muted)] block mb-1">
                🇰🇭 ខ្មែរ
              </label>
              <textarea
                className="sf-form__textarea text-sm rounded-xl w-full min-h-[5.5rem] font-khmer"
                value={treatmentKm}
                onChange={(e) => setTreatmentKm(e.target.value)}
                placeholder="របៀបព្យាបាលជំងឺនេះ?"
                lang="km"
              />
            </div>
          </div>
        </div>

        {/* Prevention Field */}
        <div
          className={`sf-card p-5 shadow-sm border transition-all ${
            preventionKm.trim()
              ? "border-amber-200 dark:border-amber-900/50"
              : "border-amber-200 dark:border-amber-900/50"
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-amber-600" />
              <h3 className="text-sm font-bold text-[var(--color-text)]">Prevention</h3>
            </div>
            {!preventionKm.trim() && (
              <span className="sf-badge sf-badge--warning text-[11px] px-2 py-0.5 inline-flex items-center gap-1 font-medium rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400">
                <AlertTriangle className="w-3 h-3" />
                <span>{t("admin.missing_km_translation")}</span>
              </span>
            )}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-[var(--color-text-muted)] block mb-1">
                🇬🇧 English
              </label>
              <textarea
                className="sf-form__textarea text-sm rounded-xl w-full min-h-[5.5rem]"
                value={preventionEn}
                onChange={(e) => setPreventionEn(e.target.value)}
                placeholder="How to prevent this disease from occurring?"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-[var(--color-text-muted)] block mb-1">
                🇰🇭 ខ្មែរ
              </label>
              <textarea
                className="sf-form__textarea text-sm rounded-xl w-full min-h-[5.5rem] font-khmer"
                value={preventionKm}
                onChange={(e) => setPreventionKm(e.target.value)}
                placeholder="របៀបការពារជំងឺនេះ?"
                lang="km"
              />
            </div>
          </div>
        </div>

        {/* Error Message */}
        {errorMessage && (
          <div className="sf-alert sf-alert--danger flex items-center gap-2" role="alert">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Submit Actions */}
        <div className="sf-card p-4 shadow-sm border border-[var(--color-border)] flex items-center justify-end gap-3">
          <Link
            to="/admin/diseases"
            className="sf-btn sf-btn--outline text-xs px-4 py-2 rounded-xl font-medium"
          >
            {t("common.cancel")}
          </Link>
          <button
            type="submit"
            className="sf-btn sf-btn--primary inline-flex items-center gap-2 text-xs px-5 py-2.5 rounded-xl font-semibold shadow-sm"
            disabled={createMutation.isPending || !nameEn.trim() || !slug.trim()}
          >
            {createMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>{t("common.saving")}</span>
              </>
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4" />
                <span>{t("admin.create_and_continue")}</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

