import type React from "react";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

interface PercentageVisualizationProps {
  /** Target percentage (0 to 100) or decimal confidence (0 to 1) */
  value: number;
  /** Variant: circular gauge, linear bar, or number only */
  variant?: "circular" | "linear" | "number";
  /** Size for circular variant (in px) */
  size?: number;
  /** Stroke width for circular variant */
  strokeWidth?: number;
  /** Show animated number label */
  showLabel?: boolean;
  /** Label underneath number in circular gauge (e.g. "Match Score") */
  sublabel?: string;
  /** Additional CSS classes */
  className?: string;
}

export function PercentageVisualization({
  value,
  variant = "circular",
  size = 110,
  strokeWidth = 9,
  showLabel = true,
  sublabel,
  className,
}: PercentageVisualizationProps): React.JSX.Element {
  // Normalize value: if <= 1 and > 0, treat as decimal ratio (e.g. 0.82 -> 82)
  const targetPercent = Math.max(
    0,
    Math.min(100, Math.round(value <= 1 && value > 0 ? value * 100 : value)),
  );

  const [displayValue, setDisplayValue] = useState<number>(() => {
    // If reduced motion is preferred, jump straight to target
    if (
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
      return targetPercent;
    }
    return 0;
  });

  useEffect(() => {
    if (typeof window === "undefined") {
      setDisplayValue(targetPercent);
      return;
    }

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setDisplayValue(targetPercent);
      return;
    }

    let startTimestamp: number | null = null;
    const duration = 900; // ms
    let animationFrameId: number;

    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      // Ease out cubic: 1 - pow(1 - progress, 3)
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayValue(Math.round(eased * targetPercent));

      if (progress < 1) {
        animationFrameId = requestAnimationFrame(step);
      } else {
        setDisplayValue(targetPercent);
      }
    };

    animationFrameId = requestAnimationFrame(step);
    return () => cancelAnimationFrame(animationFrameId);
  }, [targetPercent]);

  // Color gradient interpolation based on match confidence
  // Low (<40%): amber/muted; Mid (40-69%): primary golden; High (>=70%): vibrant emerald/teal
  const getColor = (pct: number) => {
    if (pct >= 70) return { stroke: "var(--color-secondary)", glow: "hsla(148, 55%, 38%, 0.3)" };
    if (pct >= 40) return { stroke: "var(--color-primary)", glow: "hsla(43, 90%, 48%, 0.3)" };
    return { stroke: "hsl(38, 90%, 50%)", glow: "hsla(38, 90%, 50%, 0.2)" };
  };

  const colorConfig = getColor(targetPercent);

  if (variant === "number") {
    return <span className={cn("font-bold tracking-tight", className)}>{displayValue}%</span>;
  }

  if (variant === "linear") {
    return (
      <div className={cn("w-full flex flex-col gap-1.5", className)}>
        <div className="flex justify-between items-center text-xs font-semibold">
          {sublabel && <span className="text-slate-500 dark:text-slate-400">{sublabel}</span>}
          {showLabel && (
            <span style={{ color: colorConfig.stroke }} className="ml-auto font-mono font-bold">
              {displayValue}%
            </span>
          )}
        </div>
        <div
          role="progressbar"
          aria-valuenow={targetPercent}
          aria-valuemin={0}
          aria-valuemax={100}
          className="w-full h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden p-0.5 border border-slate-200/60 dark:border-slate-700/60"
        >
          <div
            className="h-full rounded-full transition-all duration-500 ease-out"
            style={{
              width: `${String(displayValue)}%`,
              backgroundColor: colorConfig.stroke,
              boxShadow: `0 0 8px ${colorConfig.glow}`,
            }}
          />
        </div>
      </div>
    );
  }

  // Circular gauge variant
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (displayValue / 100) * circumference;

  return (
    <div
      className={cn("relative inline-flex items-center justify-center", className)}
      style={{ width: size, height: size }}
      role="progressbar"
      aria-valuenow={targetPercent}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <svg width={size} height={size} className="rotate-[-90deg] overflow-visible">
        {/* Track circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-slate-100 dark:text-slate-800/80"
        />
        {/* Animated indicator circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={colorConfig.stroke}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          style={{
            transition: "stroke-dashoffset 0.15s ease",
            filter: `drop-shadow(0 0 4px ${colorConfig.glow})`,
          }}
        />
      </svg>

      <div className="absolute inset-0 flex flex-col items-center justify-center text-center select-none">
        {showLabel && (
          <span
            className="font-bold tracking-tight text-slate-900 dark:text-slate-100"
            style={{ fontSize: size * 0.24 }}
          >
            {displayValue}
            <span className="text-[0.65em] font-medium text-slate-500 dark:text-slate-400">%</span>
          </span>
        )}
        {sublabel && (
          <span
            className="text-[0.65rem] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mt-0.5"
            style={{ fontSize: Math.max(9, size * 0.09) }}
          >
            {sublabel}
          </span>
        )}
      </div>
    </div>
  );
}
