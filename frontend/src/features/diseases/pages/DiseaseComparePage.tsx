import React, { useMemo } from "react";
import { useSearchParams, Link } from "react-router";
import { useTranslation } from "react-i18next";
import {
  Layers,
  Plus,
  X,
  Sparkles,
  ExternalLink,
  ShieldAlert,
  Leaf,
  Bug,
  TestTube,
  BookOpen,
  ArrowLeft,
  ChevronDown,
} from "lucide-react";
import { useDiseases, useDiseaseDetail } from "../hooks";
import { Skeleton } from "@/components/ui/Skeleton";
import { Badge } from "@/components/ui/Badge";
import type { DiseaseDetail, PathogenType } from "@/types/api";

const PRESETS = [
  {
    key: "preset_mildew",
    slugs: ["downy-mildew", "powdery-mildew"],
  },
  {
    key: "preset_leaf_spots",
    slugs: ["alternaria-leaf-spot", "septoria-leaf-spot"],
  },
  {
    key: "preset_stems",
    slugs: ["sclerotinia-head-rot", "phomopsis-stem-canker"],
  },
];

interface DiseaseSlotProps {
  index: number;
  slug: string;
  onSelectSlug: (slug: string) => void;
  onRemove: () => void;
  availableOptions: { slug: string; name: string; pathogen: PathogenType }[];
  isLoading?: boolean;
}

function DiseaseSlot({
  index,
  slug,
  onSelectSlug,
  onRemove,
  availableOptions,
  isLoading,
}: DiseaseSlotProps): React.JSX.Element {
  const { t } = useTranslation();

  return (
    <div className="flex-1 min-w-[260px] sf-glass-card p-4 rounded-2xl relative border-amber-500/20">
      <div className="flex items-center justify-between gap-2 mb-2">
        <span className="text-[0.65rem] uppercase font-bold tracking-wider text-slate-400 dark:text-slate-500">
          {t("compare.slot_empty", { slot: index + 1 })}
        </span>
        {slug && (
          <button
            type="button"
            onClick={onRemove}
            className="p-1 rounded-md text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors cursor-pointer"
            title={t("compare.slot_remove")}
          >
            <X size={14} />
          </button>
        )}
      </div>

      {/* Select Dropdown */}
      <div className="relative">
        <select
          value={slug}
          onChange={(e) => onSelectSlug(e.target.value)}
          aria-label={t("compare.select_disease_prompt")}
          className="w-full appearance-none py-2 px-3 pr-8 rounded-xl bg-white dark:bg-[#1A2212] border border-slate-200 dark:border-white/10 text-xs font-semibold text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-amber-500/30 transition-all cursor-pointer"
        >
          <option value="">-- {t("compare.select_disease_prompt")} --</option>
          {availableOptions.map((opt) => (
            <option key={opt.slug} value={opt.slug}>
              {opt.name} ({opt.pathogen})
            </option>
          ))}
        </select>
        <ChevronDown
          size={14}
          className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none"
        />
      </div>

      {isLoading && slug && (
        <div className="mt-3 space-y-2">
          <Skeleton height="1rem" width="80%" />
          <Skeleton height="0.8rem" width="60%" />
        </div>
      )}
    </div>
  );
}

export function DiseaseComparePage(): React.JSX.Element {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();

  // Load all published diseases for selection options
  const { data: allDiseasesData } = useDiseases({
    size: 50,
    published: true,
  });

  const availableOptions = useMemo(() => {
    if (!allDiseasesData) return [];
    return allDiseasesData.items.map((d) => ({
      slug: d.slug,
      name: d.name,
      pathogen: d.pathogen_type,
    }));
  }, [allDiseasesData]);

  // Read slugs from URL query params or defaults
  const slug1 = searchParams.get("d1") ?? "downy-mildew";
  const slug2 = searchParams.get("d2") ?? "powdery-mildew";
  const slug3 = searchParams.get("d3") ?? "";

  // Fetch individual disease details
  const { data: detail1, isLoading: loading1 } = useDiseaseDetail(slug1);
  const { data: detail2, isLoading: loading2 } = useDiseaseDetail(slug2);
  const { data: detail3, isLoading: loading3 } = useDiseaseDetail(slug3);

  const selectedSlugs = useMemo(() => {
    const list = [slug1, slug2];
    if (slug3) list.push(slug3);
    return list.filter(Boolean);
  }, [slug1, slug2, slug3]);

  const activeDetails: (DiseaseDetail | undefined)[] = useMemo(() => {
    const arr: (DiseaseDetail | undefined)[] = [];
    if (slug1) arr.push(detail1);
    if (slug2) arr.push(detail2);
    if (slug3) arr.push(detail3);
    return arr;
  }, [slug1, slug2, slug3, detail1, detail2, detail3]);

  const updateSlug = (slotIndex: number, newSlug: string) => {
    const nextParams = new URLSearchParams(searchParams);
    const key = `d${slotIndex + 1}`;
    if (newSlug) {
      nextParams.set(key, newSlug);
    } else {
      nextParams.delete(key);
    }
    setSearchParams(nextParams);
  };

  const removeSlug = (slotIndex: number) => {
    const nextParams = new URLSearchParams(searchParams);
    if (slotIndex === 0) {
      if (slug2) {
        nextParams.set("d1", slug2);
        if (slug3) {
          nextParams.set("d2", slug3);
          nextParams.delete("d3");
        } else {
          nextParams.delete("d2");
        }
      } else {
        nextParams.delete("d1");
      }
    } else if (slotIndex === 1) {
      if (slug3) {
        nextParams.set("d2", slug3);
        nextParams.delete("d3");
      } else {
        nextParams.delete("d2");
      }
    } else if (slotIndex === 2) {
      nextParams.delete("d3");
    }
    setSearchParams(nextParams);
  };

  const applyPreset = (presetSlugs: string[]) => {
    const nextParams = new URLSearchParams();
    if (presetSlugs[0]) nextParams.set("d1", presetSlugs[0]);
    if (presetSlugs[1]) nextParams.set("d2", presetSlugs[1]);
    if (presetSlugs[2]) nextParams.set("d3", presetSlugs[2]);
    setSearchParams(nextParams);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="sf-glass-card p-6 sm:p-8 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Link
                to="/diseases"
                className="p-1.5 rounded-lg text-slate-500 hover:text-amber-600 hover:bg-amber-50 dark:hover:bg-white/5 transition-colors"
                title={t("common.previous")}
              >
                <ArrowLeft size={18} />
              </Link>
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
                {t("compare.title")}
              </h1>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
              {t("compare.subtitle")}
            </p>
          </div>

          <Link
            to="/diseases"
            className="sf-btn sf-btn--secondary sf-btn--sm self-start md:self-auto flex items-center gap-1.5"
          >
            <BookOpen size={15} />
            <span>{t("landing.browse_diseases")}</span>
          </Link>
        </div>

        {/* Quick Presets Pills */}
        <div className="pt-2 border-t border-slate-200/80 dark:border-white/10 flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mr-1 flex items-center gap-1">
            <Sparkles size={13} className="text-amber-500" />
            {t("compare.preset_title")}:
          </span>
          {PRESETS.map((p) => (
            <button
              key={p.key}
              type="button"
              onClick={() => applyPreset(p.slugs)}
              className="px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 hover:bg-amber-500/20 text-amber-900 dark:text-amber-300 border border-amber-500/30 transition-all cursor-pointer"
            >
              {t(`compare.${p.key}`)}
            </button>
          ))}
        </div>
      </div>

      {/* Disease Selection Slot Bar */}
      <div className="flex flex-col sm:flex-row items-stretch gap-3">
        <DiseaseSlot
          index={0}
          slug={slug1}
          onSelectSlug={(slug) => updateSlug(0, slug)}
          onRemove={() => removeSlug(0)}
          availableOptions={availableOptions}
          isLoading={loading1}
        />

        <DiseaseSlot
          index={1}
          slug={slug2}
          onSelectSlug={(slug) => updateSlug(1, slug)}
          onRemove={() => removeSlug(1)}
          availableOptions={availableOptions}
          isLoading={loading2}
        />

        {slug3 ? (
          <DiseaseSlot
            index={2}
            slug={slug3}
            onSelectSlug={(slug) => updateSlug(2, slug)}
            onRemove={() => removeSlug(2)}
            availableOptions={availableOptions}
            isLoading={loading3}
          />
        ) : (
          <button
            type="button"
            onClick={() => {
              const unused = availableOptions.find(
                (o) => o.slug !== slug1 && o.slug !== slug2,
              );
              if (unused) updateSlug(2, unused.slug);
            }}
            className="flex-1 min-w-[200px] border-2 border-dashed border-slate-300 dark:border-white/20 hover:border-amber-500/60 rounded-2xl p-4 flex flex-col items-center justify-center gap-1.5 text-slate-500 hover:text-amber-600 dark:hover:text-amber-300 transition-all cursor-pointer group"
          >
            <Plus size={20} className="transition-transform group-hover:scale-110" />
            <span className="text-xs font-bold">{t("compare.slot_add")}</span>
          </button>
        )}
      </div>

      {/* Comparison Matrix View */}
      {selectedSlugs.length < 2 ? (
        <div className="sf-glass-card p-12 text-center rounded-2xl">
          <Layers size={36} className="mx-auto text-slate-400 mb-3" />
          <h3 className="text-base font-bold text-slate-800 dark:text-white">
            {t("compare.min_selection_notice")}
          </h3>
        </div>
      ) : (
        <div className="sf-glass-card p-0 rounded-2xl overflow-hidden border border-stone-200/80 dark:border-white/10 shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-stone-50 dark:bg-[#182010]/95 border-b border-stone-200/80 dark:border-white/10">
                  <th className="w-1/4 min-w-[180px] p-4 text-left font-bold text-xs uppercase tracking-wider text-slate-400">
                    Feature / Attribute
                  </th>
                  {selectedSlugs.map((slug, idx) => {
                    const detail = activeDetails[idx];
                    return (
                      <th
                        key={slug || idx}
                        className="p-5 text-left border-l border-stone-200/80 dark:border-white/10 min-w-[260px] w-1/3"
                      >
                        <div className="space-y-2">
                          <div className="flex items-center justify-between gap-2">
                            <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                              {detail?.name || slug}
                            </h3>
                            {detail?.pathogen_type && (
                              <Badge
                                variant={detail.pathogen_type}
                              >
                                {detail.pathogen_type}
                              </Badge>
                            )}
                          </div>

                          {detail?.image_url && (
                            <img
                              src={detail.image_url}
                              alt={detail.name}
                              className="w-full h-32 object-cover rounded-xl border border-slate-200 dark:border-white/10 shadow-xs"
                            />
                          )}

                          <Link
                            to={`/diseases/${slug}`}
                            className="inline-flex items-center gap-1 text-xs font-semibold text-amber-700 dark:text-amber-400 hover:underline"
                          >
                            <span>{t("compare.view_full_detail")}</span>
                            <ExternalLink size={12} />
                          </Link>
                        </div>
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-200/70 dark:divide-white/10 text-xs">
                {/* 1. Clinical Overview */}
                <tr className="hover:bg-amber-500/5 transition-colors">
                  <td className="p-4 font-bold text-slate-600 dark:text-slate-300 bg-stone-50/50 dark:bg-[#182010]/40">
                    <div className="flex items-center gap-1.5">
                      <BookOpen size={14} className="text-amber-500" />
                      <span>{t("compare.section_visual")}</span>
                    </div>
                  </td>
                  {selectedSlugs.map((slug, idx) => {
                    const detail = activeDetails[idx];
                    return (
                      <td
                        key={slug || idx}
                        className="p-4 border-l border-stone-200/70 dark:border-white/10 text-slate-700 dark:text-slate-300 leading-relaxed"
                      >
                        {detail?.description || t("compare.no_data")}
                      </td>
                    );
                  })}
                </tr>

                {/* 2. Pathogen & Causative Agent */}
                <tr className="hover:bg-amber-500/5 transition-colors">
                  <td className="p-4 font-bold text-slate-600 dark:text-slate-300 bg-stone-50/50 dark:bg-[#182010]/40">
                    <div className="flex items-center gap-1.5">
                      <Bug size={14} className="text-amber-500" />
                      <span>{t("compare.section_pathogen")}</span>
                    </div>
                  </td>
                  {selectedSlugs.map((slug, idx) => {
                    const detail = activeDetails[idx];
                    return (
                      <td
                        key={slug || idx}
                        className="p-4 border-l border-stone-200/70 dark:border-white/10 text-slate-700 dark:text-slate-300 leading-relaxed"
                      >
                        {detail?.cause ? (
                          <div className="font-mono text-xs">{detail.cause}</div>
                        ) : (
                          t("compare.no_data")
                        )}
                      </td>
                    );
                  })}
                </tr>

                {/* 3. Affected Plant Parts & Distinctive Symptoms */}
                <tr className="hover:bg-amber-500/5 transition-colors">
                  <td className="p-4 font-bold text-slate-600 dark:text-slate-300 bg-stone-50/50 dark:bg-[#182010]/40">
                    <div className="flex items-center gap-1.5">
                      <Leaf size={14} className="text-amber-500" />
                      <span>{t("compare.section_symptoms")}</span>
                    </div>
                  </td>
                  {selectedSlugs.map((slug, idx) => {
                    const detail = activeDetails[idx];
                    const groups = detail?.symptom_groups ?? [];
                    return (
                      <td
                        key={slug || idx}
                        className="p-4 border-l border-stone-200/70 dark:border-white/10 space-y-3"
                      >
                        {groups.length > 0 ? (
                          groups.map((grp) => (
                            <div key={grp.category.id} className="space-y-1">
                              <span className="font-bold text-[0.68rem] uppercase tracking-wider text-amber-900 dark:text-amber-300">
                                {grp.category.label}:
                              </span>
                              <div className="flex flex-wrap gap-1">
                                {grp.symptoms.map((s) => (
                                  <span
                                    key={s.symptom_id}
                                    className={`px-2 py-0.5 rounded text-[0.7rem] font-medium border ${
                                      s.is_pathognomonic || s.is_required
                                        ? "bg-amber-100 dark:bg-amber-950/60 border-amber-400 text-amber-950 dark:text-amber-200 font-bold"
                                        : "bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-300"
                                    }`}
                                  >
                                    {s.label}
                                  </span>
                                ))}
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="text-slate-400">{t("compare.no_data")}</div>
                        )}
                      </td>
                    );
                  })}
                </tr>

                {/* 4. Chemical Controls & Fungicides */}
                <tr className="hover:bg-amber-500/5 transition-colors">
                  <td className="p-4 font-bold text-slate-600 dark:text-slate-300 bg-stone-50/50 dark:bg-[#182010]/40">
                    <div className="flex items-center gap-1.5">
                      <TestTube size={14} className="text-amber-500" />
                      <span>{t("compare.section_treatments")}</span>
                    </div>
                  </td>
                  {selectedSlugs.map((slug, idx) => {
                    const detail = activeDetails[idx];
                    return (
                      <td
                        key={slug || idx}
                        className="p-4 border-l border-stone-200/70 dark:border-white/10 text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line"
                      >
                        {detail?.treatment || t("compare.no_data")}
                      </td>
                    );
                  })}
                </tr>

                {/* 5. Cultural & Prevention Controls */}
                <tr className="hover:bg-amber-500/5 transition-colors">
                  <td className="p-4 font-bold text-slate-600 dark:text-slate-300 bg-stone-50/50 dark:bg-[#182010]/40">
                    <div className="flex items-center gap-1.5">
                      <ShieldAlert size={14} className="text-amber-500" />
                      <span>{t("compare.section_prevention")}</span>
                    </div>
                  </td>
                  {selectedSlugs.map((slug, idx) => {
                    const detail = activeDetails[idx];
                    return (
                      <td
                        key={slug || idx}
                        className="p-4 border-l border-stone-200/70 dark:border-white/10 text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line"
                      >
                        {detail?.prevention || t("compare.no_data")}
                      </td>
                    );
                  })}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

