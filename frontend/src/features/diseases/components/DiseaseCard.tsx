import type React from "react";
import { Link } from "react-router";
import { ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import type { DiseaseListItem } from "@/types/api";

interface DiseaseCardProps {
  disease: DiseaseListItem;
}

/**
 * Modern Card component for the disease catalog grid.
 * Displays disease image (with fallback), name, pathogen type badge, and description with hover micro-animations.
 */
export function DiseaseCard({ disease }: DiseaseCardProps): React.JSX.Element {
  return (
    <Link
      to={`/diseases/${disease.slug}`}
      className="sf-glass-card group flex flex-col overflow-hidden text-decoration-none transition-all duration-200 hover:-translate-y-1 hover:shadow-lg border border-slate-200/80 dark:border-slate-800"
    >
      {/* Image Banner */}
      <div className="relative w-full aspect-[16/10] overflow-hidden bg-slate-100 dark:bg-stone-800/80">
        {disease.image_url ? (
          <img
            src={disease.image_url}
            alt={disease.name}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 gap-1">
            <span className="text-3xl" aria-hidden="true">
              🌻
            </span>
            <span className="text-[0.65rem] uppercase tracking-wider font-semibold">
              Sunflower Disease
            </span>
          </div>
        )}

        {/* Pathogen Floating Badge */}
        <div className="absolute top-2.5 right-2.5 shadow-sm">
          <Badge variant={disease.pathogen_type}>{disease.pathogen_type}</Badge>
        </div>
      </div>

      {/* Card Content Body */}
      <div className="p-4 sm:p-5 flex-1 flex flex-col justify-between space-y-3">
        <div className="space-y-1.5">
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors line-clamp-1">
            {disease.name}
          </h3>

          {disease.description && (
            <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed">
              {disease.description}
            </p>
          )}
        </div>

        <div className="pt-2 border-t border-slate-100 dark:border-stone-800/80 flex items-center justify-between text-xs font-semibold text-amber-600 dark:text-amber-400">
          <span>View Clinical Guide</span>
          <ArrowRight
            size={14}
            className="transition-transform duration-200 group-hover:translate-x-1"
          />
        </div>
      </div>
    </Link>
  );
}
