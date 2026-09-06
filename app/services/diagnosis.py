"""
Rule-based symptom → diagnosis helper (lightweight "expert system").

Design goals:
- Support multi-select symptoms.
- Rank multiple diseases with confidence-like scores.
- Provide "why" explanation: matched symptoms per disease.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Symptom:
    key: str
    label: str
    category: str


@dataclass(frozen=True)
class DiseaseRule:
    disease_key: str
    disease_name: str
    # symptom_key -> weight (0..1)
    weights: Dict[str, float]
    # minimum score to be considered a plausible match
    threshold: float = 0.35


# -----------------------------
# Symptom catalog (extend here)
# -----------------------------
SYMPTOMS: List[Symptom] = [
    Symptom("yellow_spots_leaves", "Yellow spots on leaves", "Leaf"),
    Symptom("white_fuzzy_mold", "White fuzzy mold", "Leaf / Head"),
    Symptom("orange_pustules", "Orange/brown rust pustules", "Leaf"),
    Symptom("dark_leaf_spots", "Dark brown/black leaf spots", "Leaf"),
    Symptom("wilting_drooping", "Wilting or drooping", "Whole plant"),
    Symptom("stem_lesions", "Brown/black spots or lesions on stem", "Stem"),
    Symptom("soft_stem_rot", "Soft/watery stem rot", "Stem"),
    Symptom("head_rot", "Rot on flower head", "Head"),
    Symptom("root_rot", "Root rot / poor roots", "Root"),
    Symptom("stunted_growth", "Stunted growth", "Whole plant"),
    Symptom("leaf_curl_mosaic", "Leaf curl / mosaic pattern", "Leaf"),
    Symptom("premature_leaf_drop", "Premature leaf drop", "Leaf"),
    Symptom("hot_dry_stress", "Hot, dry field conditions", "Environment"),
    Symptom("cool_wet_conditions", "Cool, wet conditions", "Environment"),
]

SYMPTOM_INDEX: Dict[str, Symptom] = {s.key: s for s in SYMPTOMS}


# -----------------------------------
# Disease rules (6 base diseases here)
# -----------------------------------
RULES: List[DiseaseRule] = [
    # NOTE: disease_key is the slug used in the database and in /disease/<slug> URLs.
    DiseaseRule(
        disease_key="downy-mildew",
        disease_name="Downy Mildew",
        weights={
            "yellow_spots_leaves": 0.45,
            "white_fuzzy_mold": 0.55,
            "stunted_growth": 0.35,
            "cool_wet_conditions": 0.25,
        },
        threshold=0.45,
    ),
    DiseaseRule(
        disease_key="rust",
        disease_name="Rust",
        weights={
            "orange_pustules": 0.75,
            "premature_leaf_drop": 0.25,
            "wilting_drooping": 0.10,
        },
        threshold=0.45,
    ),
    DiseaseRule(
        disease_key="alternaria-leaf-spot",
        disease_name="Alternaria Leaf Spot",
        weights={
            "dark_leaf_spots": 0.65,
            "premature_leaf_drop": 0.25,
            "yellow_spots_leaves": 0.15,
        },
        threshold=0.40,
    ),
    DiseaseRule(
        disease_key="white-mold",
        disease_name="White Mold",
        weights={
            "white_fuzzy_mold": 0.55,
            "soft_stem_rot": 0.35,
            "head_rot": 0.35,
            "wilting_drooping": 0.20,
            "cool_wet_conditions": 0.20,
        },
        threshold=0.45,
    ),
    DiseaseRule(
        disease_key="charcoal-rot",
        disease_name="Charcoal Rot",
        weights={
            "wilting_drooping": 0.40,
            "stem_lesions": 0.35,
            "root_rot": 0.20,
            "hot_dry_stress": 0.30,
        },
        threshold=0.40,
    ),
    DiseaseRule(
        disease_key="bacterial-head-rot",
        disease_name="Bacterial Head Rot",
        weights={
            "head_rot": 0.70,
            "soft_stem_rot": 0.15,
            "cool_wet_conditions": 0.15,
        },
        threshold=0.45,
    ),
]



def diagnose(selected_symptom_keys: List[str], top_k: int = 3) -> List[dict]:
    """
    Returns ranked matches:
    [
      {
        "disease_key": ...,
        "disease_name": ...,
        "score": 0..1,
        "percent": 0..100 (rounded int),
        "matched": [(label, weight), ...],
      },
      ...
    ]
    """
    selected = [k for k in selected_symptom_keys if k in SYMPTOM_INDEX]
    if not selected:
        return []

    results: List[dict] = []
    for rule in RULES:
        matched: List[Tuple[str, float]] = []
        score = 0.0
        for k in selected:
            w = rule.weights.get(k, 0.0)
            if w > 0:
                matched.append((SYMPTOM_INDEX[k].label, w))
                score += w

        # Cap at 1.0 to avoid weird >100% if many symptoms match
        score = min(1.0, score)

        if score >= rule.threshold:
            results.append(
                {
                    "disease_key": rule.disease_key,
                    "disease_name": rule.disease_name,
                    "score": score,
                    "percent": int(round(score * 100)),
                    "matched": sorted(matched, key=lambda x: x[1], reverse=True),
                }
            )

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[: max(1, top_k)]


def symptoms_grouped() -> Dict[str, List[Symptom]]:
    grouped: Dict[str, List[Symptom]] = {}
    for s in SYMPTOMS:
        grouped.setdefault(s.category, []).append(s)
    # stable ordering per category
    for cat in grouped:
        grouped[cat] = sorted(grouped[cat], key=lambda x: x.label.lower())
    return dict(sorted(grouped.items(), key=lambda x: x[0].lower()))
