import type React from "react";
import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
  /** Width as CSS value. Defaults to "100%" */
  width?: string;
  /** Height as CSS value. Defaults to "1rem" */
  height?: string;
  /** Render as a circle */
  circle?: boolean;
}

/**
 * Shimmer skeleton placeholder for loading states.
 * Uses a CSS animation defined in index.css.
 */
export function Skeleton({
  className,
  width = "100%",
  height = "1rem",
  circle = false,
}: SkeletonProps): React.JSX.Element {
  return (
    <div
      className={cn("sf-skeleton bg-stone-200/70 dark:bg-gray-700/50", className)}
      style={{
        width: circle ? height : width,
        height,
        borderRadius: circle ? "50%" : "var(--radius-md)",
      }}
      aria-hidden="true"
    />
  );
}
