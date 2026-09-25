import type React from "react";
import { cn } from "@/lib/utils";

interface ConfidenceBarProps {
  /** Value between 0 and 1 */
  value: number;
  /** Show the percentage label */
  showLabel?: boolean;
  className?: string;
  /** Size variant */
  size?: "sm" | "md" | "lg";
}

/**
 * Animated horizontal bar showing diagnosis confidence.
 * Color interpolates from red (low) → yellow (mid) → green (high).
 */
export function ConfidenceBar({
  value,
  showLabel = true,
  className,
  size = "md",
}: ConfidenceBarProps): React.JSX.Element {
  const clamped = Math.max(0, Math.min(1, value));
  const percent = Math.round(clamped * 100);

  // Hue: 0 (red) at 0%, 45 (yellow-orange) at 50%, 130 (green) at 100%
  const hue = clamped * 130;

  const heights: Record<string, string> = {
    sm: "0.375rem",
    md: "0.5rem",
    lg: "0.75rem",
  };

  return (
    <div className={cn("sf-confidence", className)}>
      <div
        className="sf-confidence__track"
        style={{ height: heights[size] }}
        role="progressbar"
        aria-valuenow={percent}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${percent}% confidence`}
      >
        <div
          className="sf-confidence__fill"
          style={{
            width: `${String(percent)}%`,
            backgroundColor: `hsl(${String(hue)}, 70%, 45%)`,
          }}
        />
      </div>
      {showLabel && <span className="sf-confidence__label">{percent}%</span>}
    </div>
  );
}
