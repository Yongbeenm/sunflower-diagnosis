"""Unit tests for the pure diagnosis scoring engine.

Part A — tested in isolation without database or models.
Each test case verifies a specific behavioral guarantee and protects against regression.
"""

from __future__ import annotations

import math

from app.services.engine.explain import build_evidence
from app.services.engine.next_question import next_best_questions
from app.services.engine.scoring import (
    DiseaseRule,
    EngineParams,
    SymptomWeight,
    rank,
    score_disease,
)

DEFAULT_PARAMS = EngineParams(
    lambda_absent=0.5,
    min_confidence=0.35,
    pathognomonic_floor=0.85,
    required_missing_penalty=0.25,
)


def test_no_answers_produces_empty_ranking() -> None:
    """Protects against phantom diagnoses when user has answered nothing."""
    rule = DiseaseRule(
        disease_id=1,
        slug="white-mold",
        symptoms=(
            SymptomWeight(symptom_id=101, weight=0.6),
            SymptomWeight(symptom_id=102, weight=0.4),
        ),
    )
    ranking = rank([rule], {}, DEFAULT_PARAMS)
    assert ranking == []


def test_one_yes_weight_score_matches_expected() -> None:
    """Protects proportional evidence accumulation: 0.55 weight on total 1.00 yields score 0.55."""
    rule = DiseaseRule(
        disease_id=1,
        slug="rust",
        symptoms=(
            SymptomWeight(symptom_id=201, weight=0.55),
            SymptomWeight(symptom_id=202, weight=0.45),
        ),
    )
    score_result = score_disease(rule, {201: "yes"}, DEFAULT_PARAMS)
    assert math.isclose(score_result.score, 0.55, rel_tol=1e-5)


def test_no_answer_reduces_score_by_lambda_absent() -> None:
    """Protects negative evidence weighting:

    A 'no' on 0.40 symptom reduces score by lambda_absent * 0.40.
    """
    rule = DiseaseRule(
        disease_id=1,
        slug="downy-mildew",
        symptoms=(
            SymptomWeight(symptom_id=301, weight=0.60),
            SymptomWeight(symptom_id=302, weight=0.40),
        ),
    )
    # 301 is yes (0.60), 302 is no (0.40)
    # raw = (0.60 - 0.5 * 0.40) / 1.00 = 0.40
    score_result = score_disease(rule, {301: "yes", 302: "no"}, DEFAULT_PARAMS)
    expected_score = 0.60 - (DEFAULT_PARAMS.lambda_absent * 0.40)
    assert math.isclose(score_result.score, expected_score, rel_tol=1e-5)


def test_pathognomonic_yes_lifts_to_floor() -> None:
    """Protects diagnostic trump symptoms:

    Pathognomonic symptom lifts a weak score to pathognomonic_floor.
    """
    rule = DiseaseRule(
        disease_id=1,
        slug="charcoal-rot",
        symptoms=(
            SymptomWeight(symptom_id=401, weight=0.10, is_pathognomonic=True),
            SymptomWeight(symptom_id=402, weight=0.90),
        ),
    )
    # Raw score is 0.10 / 1.00 = 0.10, but 401 is pathognomonic
    score_result = score_disease(rule, {401: "yes"}, DEFAULT_PARAMS)
    assert math.isclose(score_result.score, DEFAULT_PARAMS.pathognomonic_floor, rel_tol=1e-5)


def test_required_symptom_no_applies_penalty() -> None:
    """Protects mandatory symptom constraints:

    Required symptom answered 'no' multiplies score by penalty.
    """
    rule = DiseaseRule(
        disease_id=1,
        slug="phoma-black-stem",
        symptoms=(
            SymptomWeight(symptom_id=501, weight=0.80),
            SymptomWeight(symptom_id=502, weight=0.20, is_required=True),
        ),
    )
    # 501 is yes, 502 (required) is no
    # raw = (0.80 - 0.5 * 0.20) / 1.00 = 0.70
    # penalty applied: 0.70 * 0.25 = 0.175
    score_result = score_disease(rule, {501: "yes", 502: "no"}, DEFAULT_PARAMS)
    assert math.isclose(
        score_result.score, 0.70 * DEFAULT_PARAMS.required_missing_penalty, rel_tol=1e-5
    )


def test_three_symptom_disease_does_not_outrank_twelve_symptom_disease() -> None:
    """Protects against the legacy bug where matched/total scored 1/3 (0.33) over 1/12 (0.08).

    In the weighted engine, diseases are scored on absolute evidence relative to total possible
    weight, so a high-weight match on a 12-symptom disease properly outranks a low-weight match
    on a 3-symptom disease.
    """
    # 3-symptom disease where the shared symptom is weight 0.20 of 1.00
    rule_3 = DiseaseRule(
        disease_id=3,
        slug="disease-small",
        symptoms=(
            SymptomWeight(symptom_id=10, weight=0.20),
            SymptomWeight(symptom_id=11, weight=0.40),
            SymptomWeight(symptom_id=12, weight=0.40),
        ),
    )
    # 12-symptom disease where the shared symptom is weight 0.50 of 1.05
    symptoms_12 = [SymptomWeight(symptom_id=10, weight=0.50)] + [
        SymptomWeight(symptom_id=20 + i, weight=0.05) for i in range(11)
    ]
    rule_12 = DiseaseRule(
        disease_id=12,
        slug="disease-large",
        symptoms=tuple(symptoms_12),
    )

    # Legacy: rule_3 scored 1/3 = 0.33, rule_12 scored 1/12 = 0.08 (rule_3 outranked rule_12).
    # Weighted evidence: rule_12 scores 0.50 / 1.05 = 0.476, rule_3 scores 0.20 / 1.00 = 0.20.
    answers = {10: "yes"}
    score_3 = score_disease(rule_3, answers, DEFAULT_PARAMS)
    score_12 = score_disease(rule_12, answers, DEFAULT_PARAMS)

    assert score_12.score > score_3.score


def test_ties_break_deterministically_by_slug() -> None:
    """Protects ranking determinism: equal scores sort alphabetically by disease slug."""
    rule_b = DiseaseRule(
        disease_id=1,
        slug="beta-disease",
        symptoms=(SymptomWeight(symptom_id=1, weight=0.60),),
    )
    rule_a = DiseaseRule(
        disease_id=2,
        slug="alpha-disease",
        symptoms=(SymptomWeight(symptom_id=1, weight=0.60),),
    )

    ranking = rank([rule_b, rule_a], {1: "yes"}, DEFAULT_PARAMS)
    assert len(ranking) == 2
    assert ranking[0].slug == "alpha-disease"
    assert ranking[1].slug == "beta-disease"


def test_scores_stay_within_zero_to_one() -> None:
    """Protects mathematical bounds:

    Scores remain strictly within [0.0, 1.0] under extreme matches.
    """
    symptoms = tuple(SymptomWeight(symptom_id=i, weight=0.25) for i in range(10))
    rule = DiseaseRule(disease_id=1, slug="many-symptoms", symptoms=symptoms)

    all_yes = {i: "yes" for i in range(10)}
    score_yes = score_disease(rule, all_yes, DEFAULT_PARAMS)
    assert 0.0 <= score_yes.score <= 1.0

    all_no = {i: "no" for i in range(10)}
    score_no = score_disease(rule, all_no, DEFAULT_PARAMS)
    assert 0.0 <= score_no.score <= 1.0


def test_all_no_answers_produce_empty_ranking_never_negative() -> None:
    """Protects against negative scores:

    All-'no' produces an empty ranking (dropped by min_confidence).
    """
    rule = DiseaseRule(
        disease_id=1,
        slug="rust",
        symptoms=(
            SymptomWeight(symptom_id=1, weight=0.5),
            SymptomWeight(symptom_id=2, weight=0.5),
        ),
    )
    all_no = {1: "no", 2: "no"}
    single_score = score_disease(rule, all_no, DEFAULT_PARAMS)
    assert single_score.score >= 0.0

    ranking = rank([rule], all_no, DEFAULT_PARAMS)
    assert ranking == []


def test_confidence_values_sum_to_one() -> None:
    """Protects normalization contract: confidence values over returned ranking sum to 1.0."""
    rule_1 = DiseaseRule(
        disease_id=1,
        slug="rust",
        symptoms=(SymptomWeight(symptom_id=1, weight=0.7),),
    )
    rule_2 = DiseaseRule(
        disease_id=2,
        slug="white-mold",
        symptoms=(SymptomWeight(symptom_id=1, weight=0.5),),
    )
    rule_3 = DiseaseRule(
        disease_id=3,
        slug="downy-mildew",
        symptoms=(SymptomWeight(symptom_id=1, weight=0.4),),
    )

    ranking = rank([rule_1, rule_2, rule_3], {1: "yes"}, DEFAULT_PARAMS)
    assert len(ranking) == 3
    confidences = [item.confidence for item in ranking]
    assert math.isclose(sum(confidences), 1.0, rel_tol=1e-5)


def test_next_best_questions_behavior() -> None:
    """Protects adaptive interrogation:

    Never suggests answered symptoms and prefers symptoms discriminating top candidates.
    """
    # Disease A and Disease B are currently tied on symptom 1
    # Symptom 2 appears in Disease A and Disease C
    # Symptom 3 appears in Disease C and Disease D
    rule_a = DiseaseRule(
        disease_id=1,
        slug="disease-a",
        symptoms=(
            SymptomWeight(symptom_id=1, weight=0.6),
            SymptomWeight(symptom_id=2, weight=0.4),
        ),
    )
    rule_b = DiseaseRule(
        disease_id=2,
        slug="disease-b",
        symptoms=(SymptomWeight(symptom_id=1, weight=0.6),),
    )
    rule_c = DiseaseRule(
        disease_id=3,
        slug="disease-c",
        symptoms=(
            SymptomWeight(symptom_id=2, weight=0.4),
            SymptomWeight(symptom_id=3, weight=0.5),
        ),
    )
    rule_d = DiseaseRule(
        disease_id=4,
        slug="disease-d",
        symptoms=(SymptomWeight(symptom_id=3, weight=0.5),),
    )

    answers = {1: "yes"}
    questions = next_best_questions([rule_a, rule_b, rule_c, rule_d], answers, DEFAULT_PARAMS, k=3)

    suggested_ids = [q.symptom_id for q in questions]

    # 1. Never suggests symptom 1 (already answered)
    assert 1 not in suggested_ids

    # 2. Prefers symptom 2 (discriminates candidate disease A) over symptom 3
    assert len(questions) > 0
    assert questions[0].symptom_id == 2


def test_explain_never_empty_for_ranked_result() -> None:
    """Protects user evidence visibility: explanation is never empty for a ranked disease."""
    rule = DiseaseRule(
        disease_id=1,
        slug="white-mold",
        symptoms=(
            SymptomWeight(symptom_id=1, weight=0.6),
            SymptomWeight(symptom_id=2, weight=0.4),
            SymptomWeight(symptom_id=3, weight=0.2),
        ),
    )
    explanation = build_evidence(rule, {1: "yes", 2: "no"})

    assert len(explanation.supporting) == 1
    assert explanation.supporting[0].symptom_id == 1
    assert len(explanation.against) == 1
    assert explanation.against[0].symptom_id == 2
    assert (
        len(explanation.supporting) > 0
        or len(explanation.against) > 0
        or len(explanation.missing_key) > 0
    )
