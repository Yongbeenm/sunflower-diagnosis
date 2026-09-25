import type React from "react";
import { cn } from "@/lib/utils";

type BadgeVariant =
  | "default"
  | "fungal"
  | "bacterial"
  | "viral"
  | "abiotic"
  | "other"
  | "success"
  | "warning"
  | "error";

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

/**
 * Small status/category badge. Pathogen types map to named color variants.
 */
export function Badge({ children, variant = "default", className }: BadgeProps): React.JSX.Element {
  return <span className={cn("sf-badge", `sf-badge--${variant}`, className)}>{children}</span>;
}
