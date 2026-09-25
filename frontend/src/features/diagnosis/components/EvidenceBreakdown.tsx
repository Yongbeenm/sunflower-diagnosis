import type React from "react";
import { useTranslation } from "react-i18next";
import type { Evidence } from "@/types/api";

interface EvidenceBreakdownProps {
  evidence: Evidence;
}

/**
 * Shows supporting / against / missing evidence for a diagnosis result.
 * Never a bare percentage — always what matched and what didn't.
 */
export function EvidenceBreakdown({ evidence }: EvidenceBreakdownProps): React.JSX.Element {
  const { t } = useTranslation();

  const groups = [
    {
      key: "supporting" as const,
      label: t("checker.evidence_supporting"),
      items: evidence.supporting,
      variant: "supporting" as const,
    },
    {
      key: "against" as const,
      label: t("checker.evidence_against"),
      items: evidence.against,
      variant: "against" as const,
    },
    {
      key: "missing" as const,
      label: t("checker.evidence_missing"),
      items: evidence.missing_key,
      variant: "missing" as const,
    },
  ];

  return (
    <div className="sf-evidence">
      {groups.map(
        (group) =>
          group.items.length > 0 && (
            <div key={group.key} className="sf-evidence__group">
              <span className={`sf-evidence__label sf-evidence__label--${group.variant}`}>
                {group.label}
              </span>
              {group.items.map((item) => (
                <div key={item.symptom} className="sf-evidence__item">
                  <span className={`sf-evidence__dot sf-evidence__dot--${group.variant}`} />
                  <span>{item.symptom}</span>
                </div>
              ))}
            </div>
          ),
      )}
    </div>
  );
}
