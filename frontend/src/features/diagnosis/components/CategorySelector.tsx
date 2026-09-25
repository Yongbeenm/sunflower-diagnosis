import type React from "react";
import { useTranslation } from "react-i18next";
import type { LucideIcon } from "lucide-react";
import {
  Leaf,
  LeafyGreen,
  Shrub,
  Flower2,
  Wheat,
  Sprout,
  CloudSun,
  Search,
} from "lucide-react";
import type { SymptomCategory } from "@/types/api";

interface CategoryIconConfig {
  icon: LucideIcon;
  colorClass: string;
}

/** Accurate agricultural icons mapped by plant part category code using native project lucide-react */
const CATEGORY_ICONS: Record<string, CategoryIconConfig> = {
  leaf: {
    icon: Leaf,
    colorClass: "text-emerald-500 dark:text-emerald-400",
  },
  leaf_head: {
    icon: LeafyGreen,
    colorClass: "text-green-600 dark:text-green-400",
  },
  whole_plant: {
    icon: Shrub,
    colorClass: "text-emerald-600 dark:text-emerald-400",
  },
  stem: {
    icon: Shrub,
    colorClass: "text-amber-700 dark:text-amber-500",
  },
  head: {
    icon: Flower2,
    colorClass: "text-amber-500 dark:text-yellow-400",
  },
  root: {
    icon: Wheat,
    colorClass: "text-amber-800 dark:text-orange-400",
  },
  seedling: {
    icon: Sprout,
    colorClass: "text-lime-500 dark:text-lime-400",
  },
  environment: {
    icon: CloudSun,
    colorClass: "text-amber-400 dark:text-amber-300",
  },
};

interface CategorySelectorProps {
  categories: SymptomCategory[];
  activeCategoryId: number | null;
  onSelect: (categoryId: number) => void;
}

/**
 * Grid of large tap-target cards for selecting a plant part category.
 * Mobile-first: 2-column grid, expands to 4 on wider screens.
 */
export function CategorySelector({
  categories,
  activeCategoryId,
  onSelect,
}: CategorySelectorProps): React.JSX.Element {
  const { t } = useTranslation();

  return (
    <div>
      <h2 className="sf-section-title">{t("checker.select_plant_part")}</h2>
      <div className="sf-category-grid">
        {categories.map((cat) => {
          const config = CATEGORY_ICONS[cat.code];
          const IconComponent = config?.icon ?? Search;
          const colorClass = config?.colorClass ?? "text-gray-500 dark:text-gray-400";

          return (
            <button
              key={cat.id}
              type="button"
              className={`sf-category-card ${activeCategoryId === cat.id ? "sf-category-card--active" : ""}`}
              onClick={() => onSelect(cat.id)}
              aria-pressed={activeCategoryId === cat.id}
            >
              <span className="sf-category-card__icon flex items-center justify-center" aria-hidden="true">
                <IconComponent className={`w-8 h-8 ${colorClass}`} />
              </span>
              <span className="sf-category-card__label">{cat.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
