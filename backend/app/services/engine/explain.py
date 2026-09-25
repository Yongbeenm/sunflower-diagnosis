"""Evidence builder for ranked disease diagnoses.

For each ranked disease, constructs supporting, against, and missing key symptom evidence.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from app.services.engine.scoring import Answer, DiseaseRule


@dataclass(frozen=True)
class EvidenceSymptom:
    """Individual symptom evidence with its weight."""

    symptom_id: int
    weight: float


@dataclass(frozen=True)
class DiseaseExplanation:
    """Structured evidence explanation for a candidate disease."""

    disease_id: int
    supporting: tuple[EvidenceSymptom, ...]
    against: tuple[EvidenceSymptom, ...]
    missing_key: tuple[EvidenceSymptom, ...]


def build_evidence(
    rule: DiseaseRule,
    answers: Mapping[int, Answer],
) -> DiseaseExplanation:
    """Build evidence breakdown for a disease based on user answers.

    supporting:  symptoms answered "yes", weight descending
    against:     symptoms answered "no", weight descending
    missing_key: symptoms unanswered or "unknown" with weight >= 0.4, weight descending

    Never returns an empty explanation for a ranked result.
    """
    supporting: list[EvidenceSymptom] = []
    against: list[EvidenceSymptom] = []
    missing_key: list[EvidenceSymptom] = []
    all_unanswered: list[EvidenceSymptom] = []

    for sw in rule.symptoms:
        ans = answers.get(sw.symptom_id, "unknown")
        item = EvidenceSymptom(symptom_id=sw.symptom_id, weight=sw.weight)

        if ans == "yes":
            supporting.append(item)
        elif ans == "no":
            against.append(item)
        else:
            all_unanswered.append(item)
            if sw.weight >= 0.40:
                missing_key.append(item)

    supporting.sort(key=lambda item: -item.weight)
    against.sort(key=lambda item: -item.weight)
    missing_key.sort(key=lambda item: -item.weight)

    # Fallback to ensure explanation is never empty
    if not supporting and not against and not missing_key and all_unanswered:
        all_unanswered.sort(key=lambda item: -item.weight)
        missing_key.append(all_unanswered[0])

    return DiseaseExplanation(
        disease_id=rule.disease_id,
        supporting=tuple(supporting),
        against=tuple(against),
        missing_key=tuple(missing_key),
    )
