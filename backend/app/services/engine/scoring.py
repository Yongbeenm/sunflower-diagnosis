"""Pure diagnosis scoring engine.

Imports NOTHING from app.db or app.models per Hard Rule 9.
Plain frozen dataclasses in, plain frozen dataclasses out.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

Answer = Literal["yes", "no", "unknown"]


@dataclass(frozen=True)
class SymptomWeight:
    """Weight and flags for a symptom associated with a disease rule."""

    symptom_id: int
    weight: float
    is_required: bool = False
    is_pathognomonic: bool = False


@dataclass(frozen=True)
class DiseaseRule:
    """Disease candidate with its symptom weights and metadata."""

    disease_id: int
    slug: str
    symptoms: tuple[SymptomWeight, ...]


@dataclass(frozen=True)
class EngineParams:
    """Configurable scoring parameters from the active ruleset."""

    lambda_absent: float = 0.5
    min_confidence: float = 0.35
    pathognomonic_floor: float = 0.85
    required_missing_penalty: float = 0.25


@dataclass(frozen=True)
class DiseaseScore:
    """Score and normalized confidence for a ranked disease candidate."""

    disease_id: int
    slug: str
    score: float
    confidence: float = 0.0


def score_disease(
    rule: DiseaseRule,
    answers: Mapping[int, Answer],
    params: EngineParams,
) -> DiseaseScore:
    """Calculate the diagnosis score for a single candidate disease rule.

    Formula:
      present  = Σ w(s)  for s in D answered "yes"
      absent   = Σ w(s)  for s in D answered "no"
      possible = Σ w(s)  for all s in D

      raw   = (present - lambda * absent) / possible   # possible == 0 -> 0.0
      score = clamp(raw, 0, 1)

      if any pathognomonic symptom of D is "yes": score = max(score, floor)
      if any required symptom of D is "no":       score = score * penalty
    """
    present = 0.0
    absent = 0.0
    possible = 0.0
    has_pathognomonic_yes = False
    has_required_no = False

    for sw in rule.symptoms:
        possible += sw.weight
        ans = answers.get(sw.symptom_id, "unknown")

        if ans == "yes":
            present += sw.weight
            if sw.is_pathognomonic:
                has_pathognomonic_yes = True
        elif ans == "no":
            absent += sw.weight
            if sw.is_required:
                has_required_no = True

    raw = 0.0 if possible <= 0.0 else (present - params.lambda_absent * absent) / possible

    score = max(0.0, min(1.0, raw))

    if has_pathognomonic_yes:
        score = max(score, params.pathognomonic_floor)

    if has_required_no:
        score = score * params.required_missing_penalty

    return DiseaseScore(
        disease_id=rule.disease_id,
        slug=rule.slug,
        score=score,
        confidence=0.0,
    )


def rank(
    rules: Sequence[DiseaseRule],
    answers: Mapping[int, Answer],
    params: EngineParams,
) -> list[DiseaseScore]:
    """Score all rules, drop scores below min_confidence, sort, and normalize confidence.

    Sort order: score descending, then slug ascending (for deterministic tie breaks).
    Confidence: score / sum(retained scores), summing to 1.0 across retained results.
    """
    retained: list[DiseaseScore] = []

    for rule in rules:
        ds = score_disease(rule, answers, params)
        if ds.score >= params.min_confidence:
            retained.append(ds)

    if not retained:
        return []

    # Sort descending by score, ascending by slug for ties
    retained.sort(key=lambda item: (-item.score, item.slug))

    total_score = sum(item.score for item in retained)

    if total_score <= 0.0:
        return retained

    return [
        DiseaseScore(
            disease_id=item.disease_id,
            slug=item.slug,
            score=item.score,
            confidence=item.score / total_score,
        )
        for item in retained
    ]
