import type React from "react";
import { useState, useEffect, useMemo, useRef } from "react";
import { useParams, Link } from "react-router";
import { useTranslation } from "react-i18next";
import {
  ArrowLeft,
  ExternalLink,
  Leaf,
  Languages,
  Image as ImageIcon,
  CheckCircle2,
  AlertTriangle,
  Globe,
  EyeOff,
  Loader2,
} from "lucide-react";
import { useAuth } from "@/features/auth";
import { useDiseaseDetail } from "@/features/diseases/hooks";
import { useSymptomsGrouped } from "@/features/diagnosis/hooks";
import { previewDiagnosis } from "@/features/diagnosis/api";
import {
  useUpdateDisease,
  useUpdateDiseaseSymptoms,
  useUpdateDiseaseTranslations,
  useUploadMedia,
  useCreateSymptom,
} from "../hooks";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ui/ErrorState";
import type { Answer, DiagnosisResponse } from "@/types/api";

type TabKey = "content" | "symptoms" | "media";

interface LocalSymptomWeight {
  symptom_id: number;
  code: string;
  label: string;
  category_id: number;
  category_label: string;
  weight: number;
  is_required: boolean;
  is_pathognomonic: boolean;
}

export function DiseaseEditorPage(): React.JSX.Element {
  const { id: diseaseSlug } = useParams<{ id: string }>();
  const { t, i18n } = useTranslation();
  const [activeTab, setActiveTab] = useState<TabKey>("symptoms");

  const { data: disease, isLoading, isError, refetch } = useDiseaseDetail(diseaseSlug ?? "");
  const { data: groupedCatalog } = useSymptomsGrouped();

  const updateDiseaseMutation = useUpdateDisease();
  const updateSymptomsMutation = useUpdateDiseaseSymptoms();
  const updateTranslationsMutation = useUpdateDiseaseTranslations();
  const uploadMediaMutation = useUploadMedia();
  const createSymptomMutation = useCreateSymptom();
  const { user, hasPermission } = useAuth();
  const canPublish = user?.role === "admin" || hasPermission("disease:publish");

  const [publishMessage, setPublishMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const handleTogglePublish = async () => {
    if (!disease) return;
    setPublishMessage(null);
    try {
      const nextPublished = !disease.is_published;
      await updateDiseaseMutation.mutateAsync({
        id: disease.id,
        payload: { is_published: nextPublished },
      });
      setPublishMessage({
        type: "success",
        text: nextPublished ? t("admin.publish_success") : t("admin.unpublish_success"),
      });
      setTimeout(() => setPublishMessage(null), 5000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : t("admin.publish_error");
      setPublishMessage({
        type: "error",
        text: msg,
      });
    }
  };

  // -------------------------------------------------------------------------
  // Content Tab State
  // -------------------------------------------------------------------------
  const [enContent, setEnContent] = useState({
    name: "",
    description: "",
    cause: "",
    treatment: "",
    prevention: "",
  });
  const [kmContent, setKmContent] = useState({
    name: "",
    description: "",
    cause: "",
    treatment: "",
    prevention: "",
  });
  const [contentSaved, setContentSaved] = useState(false);

  // -------------------------------------------------------------------------
  // Symptoms Tab State
  // -------------------------------------------------------------------------
  const [localSymptoms, setLocalSymptoms] = useState<LocalSymptomWeight[]>([]);
  const [selectedAddSymptomId, setSelectedAddSymptomId] = useState<number | "">("");
  const [symptomsSaved, setSymptomsSaved] = useState(false);
  const [previewResult, setPreviewResult] = useState<DiagnosisResponse | null>(null);

  // Modal state for inline symptom creation
  const [showAddModal, setShowAddModal] = useState(false);
  const [newSymptomCode, setNewSymptomCode] = useState("");
  const [newSymptomLabelEn, setNewSymptomLabelEn] = useState("");
  const [newSymptomLabelKm, setNewSymptomLabelKm] = useState("");
  const [newSymptomCategoryId, setNewSymptomCategoryId] = useState<number>(1);

  // Auto-generate symptom code from label
  const generateSymptomCode = (label: string): string => {
    return label
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_|_$/g, "");
  };

  const handleNewSymptomLabelEnChange = (value: string) => {
    setNewSymptomLabelEn(value);
    setNewSymptomCode(generateSymptomCode(value));
  };

  // -------------------------------------------------------------------------
  // Media Tab State
  // -------------------------------------------------------------------------
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewMediaUrl, setPreviewMediaUrl] = useState<string | null>(null);
  const [mediaSaved, setMediaSaved] = useState(false);
  const [mediaError, setMediaError] = useState<string | null>(null);

  // Sync state when disease data arrives
  useEffect(() => {
    if (!disease) return;

    const enTr = disease.translations?.en ?? {};
    const kmTr = disease.translations?.km ?? {};

    setEnContent({
      name: enTr.name ?? disease.name ?? "",
      description: enTr.description ?? disease.description ?? "",
      cause: enTr.cause ?? disease.cause ?? "",
      treatment: enTr.treatment ?? disease.treatment ?? "",
      prevention: enTr.prevention ?? disease.prevention ?? "",
    });

    setKmContent({
      name: kmTr.name ?? "",
      description: kmTr.description ?? "",
      cause: kmTr.cause ?? "",
      treatment: kmTr.treatment ?? "",
      prevention: kmTr.prevention ?? "",
    });

    // Populate local symptoms from symptom_groups
    const items: LocalSymptomWeight[] = [];
    if (disease.symptom_groups) {
      for (const group of disease.symptom_groups) {
        for (const sym of group.symptoms) {
          items.push({
            symptom_id: sym.symptom_id,
            code: sym.code,
            label: sym.label,
            category_id: group.category.id,
            category_label: group.category.label,
            weight: Number(sym.weight),
            is_required: sym.is_required,
            is_pathognomonic: sym.is_pathognomonic,
          });
        }
      }
    }
    setLocalSymptoms(items);
  }, [disease]);

  // Live preview simulation: "If a grower reported these symptoms, where would this disease rank?"
  const abortRef = useRef<AbortController | null>(null);
  useEffect(() => {
    if (localSymptoms.length === 0 || !disease) {
      setPreviewResult(null);
      return;
    }

    if (abortRef.current) {
      abortRef.current.abort();
    }

    const controller = new AbortController();
    abortRef.current = controller;

    // Simulate grower answering "yes" to all attached symptoms
    const answers: Record<number, Answer> = {};
    for (const sym of localSymptoms) {
      answers[sym.symptom_id] = "yes";
    }

    const timer = setTimeout(() => {
      previewDiagnosis(answers, i18n.language, controller.signal)
        .then((res) => {
          setPreviewResult(res);
        })
        .catch(() => {
          // Ignore aborted
        });
    }, 400);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [localSymptoms, disease, i18n.language]);

  // Translation completeness calculation
  const fields = ["name", "description", "cause", "treatment", "prevention"] as const;
  const translatedCount = fields.filter((f) => !!kmContent[f]?.trim()).length;
  const completenessPercent = Math.round((translatedCount / fields.length) * 100);

  // Group local symptoms by category for the Symptoms tab
  const groupedLocalSymptoms = useMemo(() => {
    const map = new Map<string, LocalSymptomWeight[]>();
    for (const s of localSymptoms) {
      const cat = s.category_label || "Other";
      if (!map.has(cat)) map.set(cat, []);
      map.get(cat)?.push(s);
    }
    return Array.from(map.entries());
  }, [localSymptoms]);

  // All catalog symptoms flattened
  const allCatalogSymptoms = useMemo(() => {
    if (!groupedCatalog) return [];
    return groupedCatalog.flatMap((g) =>
      g.symptoms.map((s) => ({
        ...s,
        category_id: g.category.id,
        category_label: g.category.label,
      })),
    );
  }, [groupedCatalog]);

  // Unattached catalog symptoms for dropdown
  const unattachedCatalogSymptoms = useMemo(() => {
    const attachedIds = new Set(localSymptoms.map((s) => s.symptom_id));
    return allCatalogSymptoms.filter((s) => !attachedIds.has(s.id));
  }, [allCatalogSymptoms, localSymptoms]);

  // -------------------------------------------------------------------------
  // Handlers
  // -------------------------------------------------------------------------

  const handleSaveContent = async () => {
    if (!disease) return;
    try {
      await updateTranslationsMutation.mutateAsync({
        diseaseId: disease.id,
        locale: "en",
        fields: enContent,
      });
      await updateTranslationsMutation.mutateAsync({
        diseaseId: disease.id,
        locale: "km",
        fields: kmContent,
      });
      setContentSaved(true);
      setTimeout(() => setContentSaved(false), 2500);
    } catch {
      // Error handled
    }
  };

  const handleAddSymptom = (symptomId: number) => {
    const sym = allCatalogSymptoms.find((s) => s.id === symptomId);
    if (!sym) return;

    setLocalSymptoms((prev) => [
      ...prev,
      {
        symptom_id: sym.id,
        code: sym.code,
        label: sym.label,
        category_id: sym.category_id,
        category_label: sym.category_label,
        weight: 0.5,
        is_required: false,
        is_pathognomonic: false,
      },
    ]);
    setSelectedAddSymptomId("");
  };

  const handleInlineCreateSymptom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymptomCode.trim() || !newSymptomLabelEn.trim()) return;

    try {
      const created = await createSymptomMutation.mutateAsync({
        code: newSymptomCode.trim(),
        category_id: newSymptomCategoryId,
        label_en: newSymptomLabelEn.trim(),
        label_km: newSymptomLabelKm.trim() || undefined,
      });

      // Find the created category label
      const cat = groupedCatalog?.find((g) => g.category.id === newSymptomCategoryId);

      // Directly attach to disease
      setLocalSymptoms((prev) => [
        ...prev,
        {
          symptom_id: created.id,
          code: created.code,
          label: newSymptomLabelEn.trim(),
          category_id: newSymptomCategoryId,
          category_label: cat ? cat.category.label : "General",
          weight: 0.5,
          is_required: false,
          is_pathognomonic: false,
        },
      ]);

      setShowAddModal(false);
      setNewSymptomCode("");
      setNewSymptomLabelEn("");
      setNewSymptomLabelKm("");
    } catch {
      // Error handled
    }
  };

  const handleUpdateWeight = (symptomId: number, weight: number) => {
    setLocalSymptoms((prev) =>
      prev.map((s) => (s.symptom_id === symptomId ? { ...s, weight } : s)),
    );
  };

  const handleToggleRequired = (symptomId: number) => {
    setLocalSymptoms((prev) =>
      prev.map((s) => (s.symptom_id === symptomId ? { ...s, is_required: !s.is_required } : s)),
    );
  };

  const handleTogglePathognomonic = (symptomId: number) => {
    setLocalSymptoms((prev) =>
      prev.map((s) =>
        s.symptom_id === symptomId ? { ...s, is_pathognomonic: !s.is_pathognomonic } : s,
      ),
    );
  };

  const handleRemoveSymptom = (symptomId: number) => {
    setLocalSymptoms((prev) => prev.filter((s) => s.symptom_id !== symptomId));
  };

  const handleSaveSymptoms = async () => {
    if (!disease) return;
    try {
      await updateSymptomsMutation.mutateAsync({
        diseaseId: disease.id,
        symptoms: localSymptoms.map((s) => ({
          symptom_id: s.symptom_id,
          weight: s.weight,
          is_required: s.is_required,
          is_pathognomonic: s.is_pathognomonic,
        })),
      });
      setSymptomsSaved(true);
      setTimeout(() => setSymptomsSaved(false), 2500);
    } catch {
      // Error handled
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewMediaUrl(URL.createObjectURL(file));
    }
  };

  const [isUploadingMedia, setIsUploadingMedia] = useState(false);

  const handleSaveMedia = async () => {
    if (!selectedFile || !disease) return;
    setMediaError(null);
    setIsUploadingMedia(true);
    try {
      const media = await uploadMediaMutation.mutateAsync(selectedFile);
      await updateDiseaseMutation.mutateAsync({
        id: disease.id,
        payload: {
          media_id: media.id,
          image_media_id: media.id,
        },
      });
      setPreviewMediaUrl(media.url);
      setMediaSaved(true);
      void refetch();
      setTimeout(() => setMediaSaved(false), 3000);
    } catch (err: unknown) {
      console.error("Failed to save media:", err);
      const msg = err instanceof Error ? err.message : "Failed to upload image. Please verify file is a PNG or JPEG under 15MB.";
      setMediaError(msg);
    } finally {
      setIsUploadingMedia(false);
    }
  };

  if (isLoading) {
    return (
      <div aria-busy="true">
        <Skeleton height="2rem" width="30%" className="mb-4" />
        <Skeleton height="3rem" className="rounded-lg mb-6" />
        <Skeleton height="20rem" className="rounded-lg" />
      </div>
    );
  }

  if (isError || !disease) {
    return <ErrorState onRetry={() => void refetch()} />;
  }

  // Find simulated ranking of current disease in preview
  const previewMatch = previewResult?.results.find((r) => r.disease.id === disease.id);

  return (
    <div>
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <Link
            to="/admin/diseases"
            className="sf-btn sf-btn--ghost sf-btn--sm inline-flex items-center gap-1.5 text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text)] mb-2 px-2 py-1 rounded-lg"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>{t("admin.back_to_diseases")}</span>
          </Link>
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="sf-section-title text-2xl font-bold tracking-tight text-[var(--color-text)]">
              {disease.name}
            </h1>
            <Badge variant={disease.pathogen_type}>{disease.pathogen_type}</Badge>
            <span
              className={`sf-badge inline-flex items-center gap-1 text-xs px-2.5 py-0.5 font-medium rounded-full ${
                disease.is_published
                  ? "sf-badge--success bg-amber-500/10 text-amber-600 dark:text-amber-400"
                  : "sf-badge--warning bg-amber-500/10 text-amber-600 dark:text-amber-400"
              }`}
            >
              {disease.is_published ? (
                <CheckCircle2 className="w-3 h-3" />
              ) : (
                <AlertTriangle className="w-3 h-3" />
              )}
              <span>{disease.is_published ? t("admin.status_published") : t("admin.status_draft")}</span>
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
          {canPublish && (
            <button
              type="button"
              className={`sf-btn sf-btn--sm inline-flex items-center gap-1.5 text-xs font-semibold px-3.5 py-1.5 rounded-xl shadow-xs transition-all ${
                disease.is_published
                  ? "sf-btn--outline text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/10"
                  : "sf-btn--primary bg-amber-600 hover:bg-amber-700 text-white font-bold"
              }`}
              disabled={updateDiseaseMutation.isPending}
              onClick={() => void handleTogglePublish()}
              title={disease.is_published ? t("admin.unpublish") : t("admin.publish")}
            >
              {updateDiseaseMutation.isPending ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : disease.is_published ? (
                <EyeOff className="w-3.5 h-3.5 text-slate-500" />
              ) : (
                <Globe className="w-3.5 h-3.5 text-white" />
              )}
              <span>{disease.is_published ? t("admin.unpublish") : t("admin.publish")}</span>
            </button>
          )}

          <Link
            to={`/diseases/${disease.slug}`}
            className="sf-btn sf-btn--outline sf-btn--sm inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl shadow-xs"
            target="_blank"
            rel="noopener noreferrer"
            title="Open public grower view in a new tab"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>{t("admin.preview_public")}</span>
          </Link>
        </div>
      </div>

      {/* Publish Status Feedback Alert */}
      {publishMessage && (
        <div
          className={`sf-alert ${
            publishMessage.type === "success" ? "sf-alert--success" : "sf-alert--danger"
          } mb-4 flex items-center gap-2`}
          role="alert"
        >
          {publishMessage.type === "success" ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
          ) : (
            <AlertTriangle className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />
          )}
          <span className="text-xs sm:text-sm font-medium">{publishMessage.text}</span>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex items-center gap-2 border-b border-[var(--color-border)] mb-6 pb-2">
        <button
          type="button"
          className={`sf-admin-tab inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl transition-all ${
            activeTab === "symptoms"
              ? "sf-admin-tab--active bg-amber-500/10 text-amber-700 dark:text-amber-400 shadow-xs"
              : "text-[var(--color-text-muted)] hover:bg-[var(--color-bg-subtle)]"
          }`}
          onClick={() => setActiveTab("symptoms")}
        >
          <Leaf className="w-4 h-4" />
          <span>{t("admin.tab_symptoms")} ({localSymptoms.length})</span>
        </button>

        <button
          type="button"
          className={`sf-admin-tab inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl transition-all ${
            activeTab === "content"
              ? "sf-admin-tab--active bg-amber-500/10 text-amber-700 dark:text-amber-400 shadow-xs"
              : "text-[var(--color-text-muted)] hover:bg-[var(--color-bg-subtle)]"
          }`}
          onClick={() => setActiveTab("content")}
        >
          <Languages className="w-4 h-4" />
          <span>{t("admin.tab_content")} ({completenessPercent}%)</span>
        </button>

        <button
          type="button"
          className={`sf-admin-tab inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl transition-all ${
            activeTab === "media"
              ? "sf-admin-tab--active bg-amber-500/10 text-amber-700 dark:text-amber-400 shadow-xs"
              : "text-[var(--color-text-muted)] hover:bg-[var(--color-bg-subtle)]"
          }`}
          onClick={() => setActiveTab("media")}
        >
          <ImageIcon className="w-4 h-4" />
          <span>{t("admin.tab_media")}</span>
        </button>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* TAB 1: Symptoms (Agronomist Knowledge Base Editor)                  */}
      {/* ------------------------------------------------------------------- */}
      {activeTab === "symptoms" && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 280px",
            gap: "1.5rem",
            alignItems: "start",
          }}
        >
          <div>
            {/* Action Bar: Attach Symptom + Inline Create */}
            <div
              className="sf-card"
              style={{
                padding: "1rem",
                marginBottom: "1.5rem",
                display: "flex",
                gap: "0.75rem",
                alignItems: "center",
                flexWrap: "wrap",
              }}
            >
              <select
                className="sf-filter-select"
                style={{ flex: 1, minWidth: "220px" }}
                value={selectedAddSymptomId}
                onChange={(e) => {
                  const val = e.target.value;
                  setSelectedAddSymptomId(val ? Number(val) : "");
                  if (val) handleAddSymptom(Number(val));
                }}
              >
                <option value="">+ {t("admin.attach_symptom_placeholder")}</option>
                {unattachedCatalogSymptoms.map((s) => (
                  <option key={s.id} value={s.id}>
                    [{s.category_label}] {s.label} ({s.code})
                  </option>
                ))}
              </select>

              <button
                type="button"
                className="sf-btn sf-btn--secondary sf-btn--sm"
                onClick={() => setShowAddModal(true)}
              >
                + {t("admin.new_catalog_symptom")}
              </button>
            </div>

            {/* Grouped Symptom Rows */}
            {groupedLocalSymptoms.length === 0 ? (
              <div className="sf-card" style={{ padding: "3rem", textAlign: "center" }}>
                <p style={{ color: "var(--color-text-muted)", margin: 0 }}>
                  {t("admin.no_symptoms_attached_yet")}
                </p>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
                {groupedLocalSymptoms.map(([categoryLabel, items]) => (
                  <div key={categoryLabel} className="sf-card" style={{ padding: "1rem" }}>
                    <h3
                      style={{
                        fontSize: "0.9375rem",
                        fontWeight: 700,
                        margin: "0 0 0.75rem",
                        color: "var(--color-text)",
                      }}
                    >
                      {categoryLabel} ({items.length})
                    </h3>

                    <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                      {items.map((s) => (
                        <div
                          key={s.symptom_id}
                          style={{
                            padding: "0.75rem",
                            background: "var(--color-surface-raised)",
                            borderRadius: "var(--radius-md)",
                            display: "flex",
                            flexDirection: "column",
                            gap: "0.5rem",
                          }}
                        >
                          <div
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              alignItems: "center",
                            }}
                          >
                            <div>
                              <span
                                style={{
                                  fontWeight: 600,
                                  fontSize: "0.875rem",
                                  color: "var(--color-text)",
                                }}
                              >
                                {s.label}
                              </span>
                              <code
                                style={{
                                  fontSize: "0.75rem",
                                  color: "var(--color-text-muted)",
                                  marginLeft: "0.5rem",
                                }}
                              >
                                {s.code}
                              </code>
                            </div>

                            <button
                              type="button"
                              className="sf-btn sf-btn--ghost sf-btn--sm"
                              style={{ color: "hsl(4 80% 52%)", padding: "0.25rem 0.5rem" }}
                              onClick={() => handleRemoveSymptom(s.symptom_id)}
                              title={t("common.delete")}
                            >
                              ✕
                            </button>
                          </div>

                          {/* Controls: Weight Slider, Required, Pathognomonic */}
                          <div
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: "1.5rem",
                              flexWrap: "wrap",
                            }}
                          >
                            {/* Weight Slider */}
                            <div
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "0.5rem",
                                flex: 1,
                                minWidth: "180px",
                              }}
                            >
                              <span
                                style={{
                                  fontSize: "0.75rem",
                                  fontWeight: 600,
                                  color: "var(--color-text-muted)",
                                }}
                              >
                                Weight:
                              </span>
                              <input
                                type="range"
                                min="0"
                                max="1"
                                step="0.05"
                                value={s.weight}
                                onChange={(e) =>
                                  handleUpdateWeight(s.symptom_id, parseFloat(e.target.value))
                                }
                                style={{ flex: 1 }}
                              />
                              <span
                                style={{
                                  fontSize: "0.8125rem",
                                  fontWeight: 700,
                                  width: "2.5rem",
                                  textAlign: "right",
                                }}
                              >
                                {s.weight.toFixed(2)}
                              </span>
                            </div>

                            {/* Required toggle */}
                            <label
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "0.375rem",
                                cursor: "pointer",
                                fontSize: "0.8125rem",
                              }}
                              title={t("admin.tooltip_required")}
                            >
                              <input
                                type="checkbox"
                                checked={s.is_required}
                                onChange={() => handleToggleRequired(s.symptom_id)}
                              />
                              <span
                                style={{
                                  fontWeight: s.is_required ? 700 : 400,
                                  color: s.is_required ? "hsl(38 90% 40%)" : "inherit",
                                }}
                              >
                                {t("diseases.required_symptom")}
                              </span>
                            </label>

                            {/* Pathognomonic toggle */}
                            <label
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "0.375rem",
                                cursor: "pointer",
                                fontSize: "0.8125rem",
                              }}
                              title={t("admin.tooltip_pathognomonic")}
                            >
                              <input
                                type="checkbox"
                                checked={s.is_pathognomonic}
                                onChange={() => handleTogglePathognomonic(s.symptom_id)}
                              />
                              <span
                                style={{
                                  fontWeight: s.is_pathognomonic ? 700 : 400,
                                  color: s.is_pathognomonic ? "hsl(4 80% 52%)" : "inherit",
                                }}
                              >
                                {t("diseases.pathognomonic_symptom")}
                              </span>
                            </label>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Bottom Save Bar */}
            <div
              style={{ marginTop: "1.5rem", display: "flex", alignItems: "center", gap: "1rem" }}
            >
              <button
                type="button"
                className="sf-btn sf-btn--primary sf-btn--lg"
                disabled={updateSymptomsMutation.isPending}
                onClick={() => void handleSaveSymptoms()}
              >
                {updateSymptomsMutation.isPending ? t("common.loading") : t("common.save")}
              </button>

              {symptomsSaved && (
                <span style={{ color: "hsl(148 55% 38%)", fontWeight: 600, fontSize: "0.875rem" }}>
                  ✓ {t("admin.weights_saved_success")}
                </span>
              )}
            </div>
          </div>

          {/* Live Preview Panel */}
          <aside className="sf-card" style={{ padding: "1rem", position: "sticky", top: "1rem" }}>
            <h3
              style={{
                fontSize: "0.875rem",
                fontWeight: 700,
                margin: "0 0 0.5rem",
                color: "var(--color-primary)",
              }}
            >
              ⚡ {t("admin.live_diagnostic_preview")}
            </h3>
            <p
              style={{
                fontSize: "0.75rem",
                color: "var(--color-text-muted)",
                margin: "0 0 1rem",
                lineHeight: 1.4,
              }}
            >
              {t("admin.live_preview_explanation")}
            </p>

            {previewMatch ? (
              <div
                style={{
                  background: "var(--color-surface-raised)",
                  borderRadius: "var(--radius-md)",
                  padding: "0.75rem",
                  border: "1px solid var(--color-border)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "0.375rem",
                  }}
                >
                  <span style={{ fontSize: "0.8125rem", fontWeight: 600 }}>Simulated Rank:</span>
                  <span className="sf-candidate__rank">#{previewMatch.rank}</span>
                </div>
                <div
                  style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}
                >
                  <span style={{ fontSize: "0.8125rem", fontWeight: 600 }}>Confidence:</span>
                  <span
                    style={{ fontSize: "1rem", fontWeight: 800, color: "var(--color-primary)" }}
                  >
                    {Math.round(previewMatch.confidence * 100)}%
                  </span>
                </div>
              </div>
            ) : (
              <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", margin: 0 }}>
                {t("admin.no_preview_data")}
              </p>
            )}
          </aside>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* TAB 2: Content (Bilingual Side-by-Side Editor)                      */}
      {/* ------------------------------------------------------------------- */}
      {activeTab === "content" && (
        <div>
          {/* Completeness meter */}
          <div
            className="sf-card"
            style={{
              padding: "1rem 1.25rem",
              marginBottom: "1.5rem",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              gap: "1rem",
            }}
          >
            <div>
              <h3 style={{ fontSize: "0.9375rem", fontWeight: 700, margin: "0 0 0.25rem" }}>
                {t("admin.translation_completeness")}: {completenessPercent}%
              </h3>
              <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", margin: 0 }}>
                {t("admin.fields_translated_summary", {
                  translated: translatedCount,
                  total: fields.length,
                })}
              </p>
            </div>

            <button
              type="button"
              className="sf-btn sf-btn--primary sf-btn--sm"
              disabled={updateTranslationsMutation.isPending}
              onClick={() => void handleSaveContent()}
            >
              {updateTranslationsMutation.isPending ? t("common.loading") : t("common.save")}
            </button>
          </div>

          {/* Side by side fields */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            {fields.map((fieldKey) => {
              const isMissingKm = !kmContent[fieldKey]?.trim();
              const isLongText = fieldKey !== "name";

              return (
                <div
                  key={fieldKey}
                  className="sf-card"
                  style={{
                    padding: "1.25rem",
                    borderLeft: isMissingKm
                      ? "4px solid hsl(38 90% 48%)"
                      : "4px solid hsl(148 55% 38%)",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: "0.75rem",
                    }}
                  >
                    <h3
                      style={{
                        fontSize: "0.875rem",
                        fontWeight: 700,
                        textTransform: "capitalize",
                        margin: 0,
                      }}
                    >
                      {fieldKey.replace(/_/g, " ")}
                    </h3>
                    {isMissingKm && (
                      <span
                        className="sf-badge sf-badge--warning"
                        style={{ fontSize: "0.6875rem" }}
                      >
                        ⚠️ {t("admin.missing_km_translation")}
                      </span>
                    )}
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1rem" }}>
                    {/* English */}
                    <div>
                      <label
                        style={{
                          fontSize: "0.75rem",
                          fontWeight: 600,
                          color: "var(--color-text-muted)",
                          display: "block",
                          marginBottom: "0.25rem",
                        }}
                      >
                        🇬🇧 English
                      </label>
                      {isLongText ? (
                        <textarea
                          className="sf-form__textarea"
                          style={{ minHeight: "5rem" }}
                          value={enContent[fieldKey]}
                          onChange={(e) =>
                            setEnContent((prev) => ({ ...prev, [fieldKey]: e.target.value }))
                          }
                        />
                      ) : (
                        <input
                          type="text"
                          className="sf-form__input"
                          value={enContent[fieldKey]}
                          onChange={(e) =>
                            setEnContent((prev) => ({ ...prev, [fieldKey]: e.target.value }))
                          }
                        />
                      )}
                    </div>

                    {/* Khmer */}
                    <div>
                      <label
                        style={{
                          fontSize: "0.75rem",
                          fontWeight: 600,
                          color: "var(--color-text-muted)",
                          display: "block",
                          marginBottom: "0.25rem",
                        }}
                      >
                        🇰🇭 ភាសាខ្មែរ (Khmer)
                      </label>
                      {isLongText ? (
                        <textarea
                          className="sf-form__textarea"
                          style={{ minHeight: "5rem" }}
                          value={kmContent[fieldKey]}
                          onChange={(e) =>
                            setKmContent((prev) => ({ ...prev, [fieldKey]: e.target.value }))
                          }
                        />
                      ) : (
                        <input
                          type="text"
                          className="sf-form__input"
                          value={kmContent[fieldKey]}
                          onChange={(e) =>
                            setKmContent((prev) => ({ ...prev, [fieldKey]: e.target.value }))
                          }
                        />
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Bottom Save Bar */}
          <div style={{ marginTop: "1.5rem", display: "flex", alignItems: "center", gap: "1rem" }}>
            <button
              type="button"
              className="sf-btn sf-btn--primary sf-btn--lg"
              disabled={updateTranslationsMutation.isPending}
              onClick={() => void handleSaveContent()}
            >
              {updateTranslationsMutation.isPending ? t("common.loading") : t("common.save")}
            </button>

            {contentSaved && (
              <span style={{ color: "hsl(148 55% 38%)", fontWeight: 600, fontSize: "0.875rem" }}>
                ✓ {t("admin.content_saved_success")}
              </span>
            )}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* TAB 3: Media (Crop photo upload & preview)                          */}
      {/* ------------------------------------------------------------------- */}
      {activeTab === "media" && (
        <div className="sf-card" style={{ padding: "1.5rem", maxWidth: "36rem" }}>
          <h2 style={{ fontSize: "1.125rem", fontWeight: 700, margin: "0 0 1rem" }}>
            {t("admin.disease_media_title")}
          </h2>

          <div style={{ marginBottom: "1.5rem" }}>
            <span
              style={{
                fontSize: "0.8125rem",
                fontWeight: 600,
                display: "block",
                marginBottom: "0.5rem",
              }}
            >
              {t("admin.current_image")}:
            </span>
            {previewMediaUrl || disease.image_url ? (
              <img
                src={previewMediaUrl ?? disease.image_url ?? ""}
                alt={disease.name}
                style={{
                  width: "100%",
                  maxHeight: "16rem",
                  objectFit: "cover",
                  borderRadius: "var(--radius-md)",
                }}
              />
            ) : (
              <div
                style={{
                  height: "10rem",
                  background: "var(--color-surface-raised)",
                  borderRadius: "var(--radius-md)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "var(--color-text-muted)",
                }}
              >
                {t("admin.no_image_uploaded")}
              </div>
            )}
          </div>

          <div className="sf-form__group">
            <label htmlFor="media-upload" className="sf-form__label">
              {t("admin.upload_new_image")}
            </label>
            <input
              id="media-upload"
              type="file"
              accept="image/png,image/jpeg"
              onChange={handleFileChange}
              style={{ fontSize: "0.875rem" }}
            />
            <small
              style={{ color: "var(--color-text-muted)", display: "block", marginTop: "0.25rem" }}
            >
              PNG or JPEG only, max 15MB. EXIF stripped automatically.
            </small>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginTop: "1.5rem" }}>
            <button
              type="button"
              className="sf-btn sf-btn--primary sf-btn--sm inline-flex items-center gap-1.5"
              disabled={
                !selectedFile ||
                isUploadingMedia ||
                uploadMediaMutation.isPending ||
                updateDiseaseMutation.isPending
              }
              onClick={() => void handleSaveMedia()}
            >
              {isUploadingMedia ||
              uploadMediaMutation.isPending ||
              updateDiseaseMutation.isPending ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>{t("common.loading")}</span>
                </>
              ) : (
                <span>{t("admin.upload_and_save")}</span>
              )}
            </button>

            {mediaSaved && (
              <span style={{ color: "hsl(148 55% 38%)", fontWeight: 600, fontSize: "0.875rem" }}>
                ✓ {t("admin.media_saved_success")}
              </span>
            )}

            {mediaError && (
              <span style={{ color: "var(--color-danger, #ef4444)", fontWeight: 600, fontSize: "0.875rem" }}>
                ⚠ {mediaError}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Inline Modal to Create Symptom in Catalog */}
      {showAddModal && (
        <div
          role="dialog"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 100,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            padding: "1rem",
          }}
        >
          <form
            onSubmit={(e) => void handleInlineCreateSymptom(e)}
            className="sf-card"
            style={{ width: "100%", maxWidth: "24rem", padding: "1.5rem" }}
          >
            <h3 style={{ margin: "0 0 1rem", fontSize: "1rem", fontWeight: 700 }}>
              {t("admin.new_catalog_symptom")}
            </h3>

            {/* Code field hidden - auto-generated from label */}

            {/* Side-by-side English and Khmer labels */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1rem", marginBottom: "1rem" }}>
              <div className="sf-form__group">
                <label htmlFor="symptom-label-en" className="sf-form__label">
                  🇬🇧 Label (English) *
                </label>
                <input
                  id="symptom-label-en"
                  type="text"
                  required
                  className="sf-form__input"
                  placeholder="e.g. Yellowing between leaf veins"
                  value={newSymptomLabelEn}
                  onChange={(e) => handleNewSymptomLabelEnChange(e.target.value)}
                />
                {newSymptomCode && (
                  <p style={{ fontSize: "0.75rem", color: "hsl(0 0% 60%)", marginTop: "0.25rem" }}>
                    {t("admin.auto_code")}: <code>{newSymptomCode}</code>
                  </p>
                )}
              </div>

              <div className="sf-form__group">
                <label htmlFor="symptom-label-km" className="sf-form__label">
                  🇰🇭 Label (ខ្មែរ)
                </label>
                <input
                  id="symptom-label-km"
                  type="text"
                  className="sf-form__input"
                  placeholder="e.g. ស្លឹកពណ៌លឿងរវាងសរសៃ"
                  value={newSymptomLabelKm}
                  onChange={(e) => setNewSymptomLabelKm(e.target.value)}
                  lang="km"
                  style={{ fontFamily: "'Noto Sans Khmer', sans-serif" }}
                />
              </div>
            </div>

            <div className="sf-form__group">
              <label htmlFor="symptom-category" className="sf-form__label">
                Plant Part *
              </label>
              <select
                id="symptom-category"
                className="sf-filter-select"
                style={{ width: "100%" }}
                value={newSymptomCategoryId}
                onChange={(e) => setNewSymptomCategoryId(Number(e.target.value))}
              >
                {groupedCatalog?.map((g) => (
                  <option key={g.category.id} value={g.category.id}>
                    {g.category.label}
                  </option>
                ))}
              </select>
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                gap: "0.5rem",
                marginTop: "1.5rem",
              }}
            >
              <button
                type="button"
                className="sf-btn sf-btn--ghost sf-btn--sm"
                onClick={() => setShowAddModal(false)}
              >
                {t("common.cancel")}
              </button>
              <button
                type="submit"
                className="sf-btn sf-btn--primary sf-btn--sm"
                disabled={createSymptomMutation.isPending}
              >
                {createSymptomMutation.isPending ? t("common.loading") : t("common.save")}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
