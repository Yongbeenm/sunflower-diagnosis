"""Information-gain next-best-question selector.

Finds the unanswered symptoms whose answers would most reduce uncertainty
(Shannon entropy) across candidate diseases.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from app.services.engine.scoring import Answer, DiseaseRule, EngineParams, rank


@dataclass(frozen=True)
class NextQuestion:
    """Suggested symptom question with expected information gain."""

    symptom_id: int
    information_gain: float


def calculate_entropy(confidences: Sequence[float]) -> float:
    """Calculate Shannon entropy of a confidence distribution in bits.

    H(P) = - Σ p_i * log2(p_i) for p_i > 0
    """
    total = sum(confidences)
    if total <= 0.0:
        return 0.0

    h = 0.0
    for c in confidences:
        if c > 0.0:
            p = c / total
            h -= p * math.log2(p)
    return h


def next_best_questions(
    rules: Sequence[DiseaseRule],
    answers: Mapping[int, Answer],
    params: EngineParams,
    k: int = 3,
) -> list[NextQuestion]:
    """Select top k unanswered symptoms ranked by expected information gain.

    1. Never suggests an already-answered symptom.
    2. Ignores symptoms appearing in only one candidate rule (cannot discriminate).
    3. For each candidate symptom, simulates answering 'yes' and 'no',
       measures the change in confidence distribution entropy, and returns
       top k by expected gain.
    4. Prioritizes high-weight symptoms (pathognomonic, high-discrimination).
    """
    if not rules:
        return []

    # Current ranking and its baseline entropy
    current_ranking = rank(rules, answers, params)
    h_curr = calculate_entropy([d.confidence for d in current_ranking])

    # Count appearances of symptoms across rules and track max weight
    symptom_rule_counts: Counter[int] = Counter()
    symptom_max_weight: dict[int, float] = {}
    
    for rule in rules:
        for sw in rule.symptoms:
            symptom_rule_counts[sw.symptom_id] += 1
            # Track highest weight for this symptom across all diseases
            current_max = symptom_max_weight.get(sw.symptom_id, 0.0)
            symptom_max_weight[sw.symptom_id] = max(current_max, sw.weight)

    # Candidate symptoms: unanswered and appearing in > 1 rule
    candidates: list[int] = []
    for symptom_id, count in symptom_rule_counts.items():
        ans = answers.get(symptom_id)
        if ans in ("yes", "no"):
            # Never suggest an already-answered symptom
            continue
        if count <= 1:
            # Ignore symptoms appearing in only one rule (cannot discriminate)
            continue
        candidates.append(symptom_id)

    scored_questions: list[NextQuestion] = []

    for symptom_id in candidates:
        # Simulation 1: symptom answered 'yes'
        answers_yes = {**answers, symptom_id: "yes"}
        rank_yes = rank(rules, answers_yes, params)
        h_yes = calculate_entropy([d.confidence for d in rank_yes])

        # Simulation 2: symptom answered 'no'
        answers_no = {**answers, symptom_id: "no"}
        rank_no = rank(rules, answers_no, params)
        h_no = calculate_entropy([d.confidence for d in rank_no])

        # Expected entropy after answering
        h_exp = 0.5 * h_yes + 0.5 * h_no

        # Expected information gain = reduction in entropy
        # If baseline entropy is 0 (e.g. no prior answers), measure distribution differentiation
        if h_curr > 0.0:
            gain = h_curr - h_exp
        else:
            # When no baseline, prefer symptoms that differentiate candidates
            gain = abs(h_yes - h_no) if (h_yes > 0.0 or h_no > 0.0) else 0.0
        
        # Boost gain by symptom weight (high-value symptoms asked first)
        # Weight ranges 0.5-1.0, so this adds 10-20% bonus to high-weight symptoms
        weight_boost = symptom_max_weight.get(symptom_id, 0.5)
        adjusted_gain = gain * (1.0 + 0.2 * weight_boost)

        scored_questions.append(
            NextQuestion(
                symptom_id=symptom_id,
                information_gain=round(max(0.0, adjusted_gain), 4),
            )
        )

    # Sort descending by information gain, ascending by symptom_id for deterministic ties
    scored_questions.sort(key=lambda q: (-q.information_gain, q.symptom_id))

    return scored_questions[:k]
