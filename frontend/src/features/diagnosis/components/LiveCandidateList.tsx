import type React from "react";
import { useTranslation } from "react-i18next";
import { ConfidenceBar } from "@/components/ui/ConfidenceBar";
import type { DiagnosisResult } from "@/types/api";

interface LiveCandidateListProps {
  results: DiagnosisResult[];
  isLoading?: boolean;
}

/**
 * Live-updating ranked candidate list with confidence bars.
 * Uses aria-live="polite" so screen readers announce updates.
 */
export function LiveCandidateList({
  results,
  isLoading = false,
}: LiveCandidateListProps): React.JSX.Element {
  const { t } = useTranslation();

  if (results.length === 0 && !isLoading) {
    return (
      <div className="sf-candidates" aria-live="polite">
        <p
          style={{
            color: "var(--color-text-muted)",
            fontSize: "0.875rem",
            textAlign: "center",
            padding: "1rem",
          }}
        >
          {t("checker.no_candidates_yet")}
        </p>
      </div>
    );
  }

  return (
    <div className="sf-candidates" aria-live="polite" aria-label={t("checker.candidate_list")}>
      {isLoading && (
        <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", textAlign: "center" }}>
          {t("common.loading")}
        </p>
      )}
      {results.map((result) => (
        <div key={result.disease.slug} className="sf-candidate">
          <div className="sf-candidate__header">
            <span className="sf-candidate__name">{result.disease.name}</span>
            <span className="sf-candidate__rank">#{String(result.rank)}</span>
          </div>
          <ConfidenceBar value={result.confidence} size="sm" />
        </div>
      ))}
    </div>
  );
}
