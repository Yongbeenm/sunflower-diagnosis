import type React from "react";
import { cn } from "@/lib/utils";
import { Search } from "lucide-react";

interface EmptyStateProps {
  className?: string;
  icon?: React.ReactNode | string;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

/**
 * Illustrated empty state with configurable message and optional CTA.
 */
export function EmptyState({
  className,
  icon,
  title,
  description,
  action,
}: EmptyStateProps): React.JSX.Element {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center text-center p-8 sm:p-12 sf-glass-card space-y-3",
        className,
      )}
    >
      <div className="w-14 h-14 rounded-2xl bg-amber-500/10 dark:bg-amber-400/10 text-amber-600 dark:text-amber-400 flex items-center justify-center text-2xl shadow-inner border border-amber-500/20">
        {icon ? (
          typeof icon === "string" && icon.length > 2 ? (
            <span>{icon}</span>
          ) : (
            icon
          )
        ) : (
          <Search size={26} />
        )}
      </div>

      <div className="space-y-1 max-w-sm">
        <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">{title}</h3>
        {description && (
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
            {description}
          </p>
        )}
      </div>

      {action && <div className="pt-2">{action}</div>}
    </div>
  );
}
