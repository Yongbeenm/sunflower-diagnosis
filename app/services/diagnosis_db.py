from __future__ import annotations

from typing import Dict, List, Tuple

from app.models.disease import Disease

# Compatibility: results match the old diagnosis.py shape:
# {disease_key, disease_name, score, percent, matched:[(label, weight), ...]}

DEFAULT_THRESHOLD = 0.40  # works well for checklist-based matching


def _all_symptom_items() -> list[dict]:
    """Union of checklist items across all diseases.

    Returns list of {key,label,category}.
    """
    diseases = Disease.query.order_by(Disease.name.asc()).all()
    seen: set[str] = set()
    items: list[dict] = []
    for d in diseases:
        for it in (d.checklist_items() or []):
            key = (it.get("key") or "").strip()
            label = (it.get("label") or "").strip()
            label_km = (it.get("label_km") or "").strip() or label
            category = (it.get("category") or "General").strip() or "General"
            if not key or not label or key in seen:
                continue
            seen.add(key)
            items.append({"key": key, "label": label, "label_km": label_km, "category": category})
    return items


def symptoms_grouped() -> Dict[str, List[dict]]:
    items = _all_symptom_items()
    grouped: Dict[str, List[dict]] = {}
    for s in items:
        grouped.setdefault(s.get("category") or "General", []).append(s)
    # stable ordering
    for cat in grouped:
        grouped[cat] = sorted(grouped[cat], key=lambda x: (x.get("label") or "").lower())
    return dict(sorted(grouped.items(), key=lambda x: x[0].lower()))


def symptom_index() -> Dict[str, dict]:
    return {s["key"]: s for s in _all_symptom_items()}


def diagnose(selected_keys: List[str], top_k: int = 3) -> List[dict]:
    selected_keys = [k for k in (selected_keys or []) if k]
    selected_set = set(selected_keys)

    diseases = Disease.query.order_by(Disease.name.asc()).all()
    results: List[dict] = []

    for d in diseases:
        disease_symptoms = [it.get("key") for it in (d.checklist_items() or []) if it.get("key")]
        if not disease_symptoms:
            # If a disease has no checklist configured, skip it from diagnosis ranking.
            continue

        total = len(disease_symptoms)
        matched_keys = [k for k in disease_symptoms if k in selected_set]
        matched = len(matched_keys)

        score = matched / float(total) if total else 0.0
        if score < DEFAULT_THRESHOLD:
            continue

        percent = int(round(score * 100))
        # For explanation, return labels with a constant weight = 1.0 (checklist).
        idx = symptom_index()
        matched_pairs: List[Tuple[str, float]] = []
        for k in matched_keys:
            s = idx.get(k)
            if s:
                matched_pairs.append((s.get("label"), 1.0))

        results.append(
            {
                "disease_id": d.id,
                "disease_key": d.slug,
                "disease_name": d.name,
                "score": float(score),
                "percent": percent,
                "matched": matched_pairs,
            }
        )

    # Sort by score desc, then percent desc, then name
    results.sort(key=lambda r: (-r["score"], -r["percent"], r["disease_name"]))
    return results[: max(1, int(top_k or 3))]
