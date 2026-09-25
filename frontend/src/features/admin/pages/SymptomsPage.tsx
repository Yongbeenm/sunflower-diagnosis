import type React from "react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Plus,
  Pencil,
  Trash2,
  Leaf,
  Search,
  X,
  Loader2,
} from "lucide-react";
import { useSymptomsGrouped } from "@/features/diagnosis/hooks";
import { useCreateSymptom, useUpdateSymptom, useDeleteSymptom } from "../hooks";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ui/ErrorState";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import type { SymptomItem } from "@/types/api";

interface ExtendedSymptom extends SymptomItem {
  category_id: number;
  category_label: string;
}

export function SymptomsPage(): React.JSX.Element {
  const { t } = useTranslation();
  const { data: grouped, isLoading, isError, refetch } = useSymptomsGrouped();

  const createMutation = useCreateSymptom();
  const updateMutation = useUpdateSymptom();
  const deleteMutation = useDeleteSymptom();

  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("");

  // Edit / Create state
  const [editingSymptom, setEditingSymptom] = useState<ExtendedSymptom | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [formCode, setFormCode] = useState("");
  const [formLabelEn, setFormLabelEn] = useState("");
  const [formLabelKm, setFormLabelKm] = useState("");
  const [formCategoryId, setFormCategoryId] = useState<number>(1);
  const [formError, setFormError] = useState<string | null>(null);

  // Delete state
  const [symptomToDelete, setSymptomToDelete] = useState<ExtendedSymptom | null>(null);
  const [conflictError, setConflictError] = useState<string | null>(null);

  // Flatten grouped symptoms
  const allSymptoms: ExtendedSymptom[] = (grouped ?? []).flatMap((g) =>
    g.symptoms.map((s) => ({
      ...s,
      category_id: g.category.id,
      category_label: g.category.label,
    })),
  );

  const filtered = allSymptoms.filter((s) => {
    const matchesQuery =
      !search ||
      s.label.toLowerCase().includes(search.toLowerCase()) ||
      s.code.toLowerCase().includes(search.toLowerCase());
    const matchesCat = !selectedCategory || String(s.category_id) === selectedCategory;
    return matchesQuery && matchesCat;
  });

  // Auto-generate code from label
  const generateCode = (label: string): string => {
    return label
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_|_$/g, "");
  };

  const openCreateModal = () => {
    setFormCode("");
    setFormLabelEn("");
    setFormLabelKm("");
    setFormCategoryId(grouped?.[0]?.category.id ?? 1);
    setFormError(null);
    setIsCreating(true);
  };

  const openEditModal = (s: ExtendedSymptom) => {
    setEditingSymptom(s);
    setFormCode(s.code);
    setFormLabelEn(s.label);
    setFormLabelKm("");
    setFormCategoryId(s.category_id);
    setFormError(null);
  };

  const handleLabelEnChange = (value: string) => {
    setFormLabelEn(value);
    if (isCreating) {
      setFormCode(generateCode(value));
    }
  };

  const handleSaveForm = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formCode.trim() || !formLabelEn.trim()) return;

    setFormError(null);
    try {
      if (isCreating) {
        await createMutation.mutateAsync({
          code: formCode.trim(),
          label_en: formLabelEn.trim(),
          label_km: formLabelKm.trim() || undefined,
          category_id: formCategoryId,
        });
        setIsCreating(false);
      } else if (editingSymptom) {
        await updateMutation.mutateAsync({
          id: editingSymptom.id,
          payload: {
            code: formCode.trim(),
            label_en: formLabelEn.trim(),
            label_km: formLabelKm.trim() || undefined,
            category_id: formCategoryId,
          },
        });
        setEditingSymptom(null);
      }
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : t("common.error"));
    }
  };

  const handleDelete = async () => {
    if (!symptomToDelete) return;
    setConflictError(null);
    try {
      await deleteMutation.mutateAsync(symptomToDelete.id);
      setSymptomToDelete(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : t("common.error");
      setConflictError(msg);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Leaf size={22} className="text-amber-500" />
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
              {t("admin.symptoms_catalog_title")}
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
            {t("admin.symptoms_catalog_subtitle")}
          </p>
        </div>

        <button
          type="button"
          className="sf-btn sf-btn--primary sf-btn--sm self-start sm:self-auto flex items-center gap-1.5 font-bold shadow-xs"
          onClick={openCreateModal}
        >
          <Plus size={16} />
          <span>{t("admin.add_symptom")}</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="sf-glass-card p-4 flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            className="w-full pl-9 pr-3.5 py-2 text-xs sm:text-sm rounded-xl bg-white dark:bg-stone-900/70 border border-slate-200 dark:border-slate-700 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all"
            placeholder={t("admin.search_symptoms_placeholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <select
          className="w-full sm:w-auto px-3 py-2 text-xs sm:text-sm rounded-xl bg-white dark:bg-stone-900/70 border border-slate-200 dark:border-slate-700 focus:border-amber-500 outline-none transition-all"
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          <option value="">{t("admin.all_plant_parts")}</option>
          {grouped?.map((g) => (
            <option key={g.category.id} value={String(g.category.id)}>
              {g.category.label}
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div aria-busy="true" className="space-y-2">
          <Skeleton height="3rem" className="rounded-xl" />
          <Skeleton height="15rem" className="rounded-xl" />
        </div>
      ) : isError ? (
        <ErrorState onRetry={() => void refetch()} />
      ) : (
        <div className="sf-glass-card overflow-hidden border border-slate-200/80 dark:border-slate-800">
          <div className="overflow-x-auto">
            <table className="sf-table">
              <thead>
                <tr>
                  <th>{t("admin.col_label")}</th>
                  <th>{t("admin.col_code")}</th>
                  <th>{t("admin.col_category")}</th>
                  <th style={{ textAlign: "right" }}>{t("admin.col_actions")}</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((s) => (
                  <tr key={s.id}>
                    <td className="font-semibold text-slate-900 dark:text-slate-100">{s.label}</td>
                    <td>
                      <code className="text-[0.75rem] font-mono text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded">
                        {s.code}
                      </code>
                    </td>
                    <td>
                      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                        {s.category_label}
                      </span>
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <div className="inline-flex items-center gap-1.5 justify-end">
                        <button
                          type="button"
                          className="sf-btn sf-btn--secondary sf-btn--sm text-xs flex items-center gap-1"
                          onClick={() => openEditModal(s)}
                        >
                          <Pencil size={13} />
                          <span className="hidden md:inline">{t("admin.edit")}</span>
                        </button>
                        <button
                          type="button"
                          className="sf-btn sf-btn--ghost sf-btn--sm text-xs text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/50"
                          onClick={() => {
                            setConflictError(null);
                            setSymptomToDelete(s);
                          }}
                          title={t("common.delete")}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create / Edit Modal Dialog */}
      {(isCreating || editingSymptom) && (
        <div
          role="dialog"
          aria-modal="true"
          className="sf-modal-backdrop"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setIsCreating(false);
              setEditingSymptom(null);
            }
          }}
        >
          <form
            onSubmit={(e) => void handleSaveForm(e)}
            className="sf-card max-w-lg w-full p-6 space-y-5 shadow-2xl border border-slate-200 dark:border-slate-800 animate-in fade-in zoom-in-95 duration-150"
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <Leaf size={18} className="text-amber-500" />
                <span>{isCreating ? t("admin.add_symptom") : t("admin.edit_symptom")}</span>
              </h3>
              <button
                type="button"
                onClick={() => {
                  setIsCreating(false);
                  setEditingSymptom(null);
                }}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1"
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                <div className="space-y-1.5">
                  <label htmlFor="modal-symptom-label-en" className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                    🇬🇧 {t("admin.col_label")} (English) *
                  </label>
                  <input
                    id="modal-symptom-label-en"
                    type="text"
                    required
                    className="w-full px-3.5 py-2 text-xs sm:text-sm rounded-xl bg-white dark:bg-stone-900/70 border border-slate-200 dark:border-slate-700 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all"
                    placeholder="e.g. Raised reddish pustules"
                    value={formLabelEn}
                    onChange={(e) => handleLabelEnChange(e.target.value)}
                  />
                  {isCreating && formCode && (
                    <p className="text-[0.7rem] text-slate-400 font-mono">
                      {t("admin.auto_code")}: <code className="bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded">{formCode}</code>
                    </p>
                  )}
                </div>

                <div className="space-y-1.5">
                  <label htmlFor="modal-symptom-label-km" className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                    🇰🇭 {t("admin.col_label")} (ខ្មែរ)
                  </label>
                  <input
                    id="modal-symptom-label-km"
                    type="text"
                    className="w-full px-3.5 py-2 text-xs sm:text-sm rounded-xl bg-white dark:bg-stone-900/70 border border-slate-200 dark:border-slate-700 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all font-khmer"
                    placeholder="e.g. ដំបៅពណ៌ត្នោតលើស្លឹក"
                    value={formLabelKm}
                    onChange={(e) => setFormLabelKm(e.target.value)}
                    lang="km"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label htmlFor="modal-symptom-category" className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                  {t("admin.col_category")} *
                </label>
                <select
                  id="modal-symptom-category"
                  className="w-full px-3.5 py-2 text-xs sm:text-sm rounded-xl bg-white dark:bg-stone-900/70 border border-slate-200 dark:border-slate-700 focus:border-amber-500 outline-none transition-all"
                  value={formCategoryId}
                  onChange={(e) => setFormCategoryId(Number(e.target.value))}
                >
                  {grouped?.map((g) => (
                    <option key={g.category.id} value={g.category.id}>
                      {g.category.label}
                    </option>
                  ))}
                </select>
              </div>

              {formError && (
                <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900 text-xs text-rose-700 dark:text-rose-300 font-medium">
                  {formError}
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100 dark:border-slate-800">
              <button
                type="button"
                className="sf-btn sf-btn--ghost sf-btn--sm text-xs"
                onClick={() => {
                  setIsCreating(false);
                  setEditingSymptom(null);
                }}
              >
                {t("common.cancel")}
              </button>
              <button
                type="submit"
                className="sf-btn sf-btn--primary sf-btn--sm text-xs font-bold flex items-center gap-1.5"
                disabled={createMutation.isPending || updateMutation.isPending}
              >
                {(createMutation.isPending || updateMutation.isPending) && (
                  <Loader2 size={13} className="animate-spin" />
                )}
                <span>{t("common.save")}</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={symptomToDelete !== null}
        title={t("admin.confirm_delete_symptom_title")}
        message={
          conflictError
            ? `⚠️ Cannot delete: ${conflictError}`
            : t("admin.confirm_delete_symptom_desc", { label: symptomToDelete?.label ?? "" })
        }
        confirmLabel={t("common.delete")}
        isDanger={true}
        isLoading={deleteMutation.isPending}
        onConfirm={() => void handleDelete()}
        onCancel={() => {
          setSymptomToDelete(null);
          setConflictError(null);
        }}
      />
    </div>
  );
}
