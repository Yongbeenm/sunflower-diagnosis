from __future__ import annotations

import json
import re
from datetime import datetime

from extensions import db
from app.models.symptom_catalog import SymptomCatalog
from app.services.disease_helpers import keyify

DEFAULT_CATEGORY = "General"
SYNC_DEFAULT_CATEGORY = "Environment"

_CATEGORY_CANONICAL = {
    "leaf": "Leaf",
    "leafhead": "Leaf / Head",
    "wholeplant": "Whole plant",
    "stem": "Stem",
    "head": "Head",
    "root": "Root",
    "seed": "Seed / Seedling",
    "seedling": "Seed / Seedling",
    "seedseedling": "Seed / Seedling",
    "environment": "Environment",
    "env": "Environment",
    "environmental": "Environment",
    "general": "General",
}

CHECKLIST_CATEGORY_CHOICES = [
    ("Leaf", "Leaf"),
    ("Leaf / Head", "Leaf / Head"),
    ("Whole plant", "Whole plant"),
    ("Stem", "Stem"),
    ("Head", "Head"),
    ("Root", "Root"),
    ("Seed / Seedling", "Seed / Seedling"),
    ("Environment", "Environment"),
]

SYSTEM_SYMPTOM_CATEGORY_CHOICES = CHECKLIST_CATEGORY_CHOICES + [
    ("General", "General"),
]


def _norm(value: str) -> str:
    return (value or "").strip().lower()


def canonical_category(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return DEFAULT_CATEGORY
    key = re.sub(r"[^a-z0-9]+", "", raw.lower())
    return _CATEGORY_CANONICAL.get(key, raw)


def _normalize_items(items: list[dict]) -> list[dict]:
    out: list[dict] = []
    for item in items or []:
        if isinstance(item, dict):
            label = (item.get("label") or "").strip()
            label_km = (item.get("label_km") or "").strip() or label
            category = canonical_category(item.get("category") or DEFAULT_CATEGORY)
            key = (item.get("key") or "").strip() or keyify(label)
        else:
            label = str(item).strip()
            label_km = label
            category = DEFAULT_CATEGORY
            key = keyify(label)

        if not label:
            continue
        out.append({"key": key, "label": label, "label_km": label_km, "category": category})
    return out


def _unique_keyed_items(items: list[dict]) -> list[dict]:
    # Remove exact duplicates by category+label (case-insensitive), then ensure unique keys.
    seen_label_cat: set[tuple[str, str]] = set()
    deduped: list[dict] = []
    for item in items:
        pair = (_norm(item.get("category")), _norm(item.get("label")))
        if pair in seen_label_cat:
            continue
        seen_label_cat.add(pair)
        deduped.append(item)

    seen_keys: set[str] = set()
    out: list[dict] = []
    for item in deduped:
        base_key = (item.get("key") or "").strip() or keyify(item["label"])
        key = base_key
        i = 1
        while key in seen_keys:
            i += 1
            key = f"{base_key}_{i}"
        seen_keys.add(key)
        out.append(
            {
                "key": key,
                "label": item["label"],
                "label_km": (item.get("label_km") or item["label"]).strip(),
                "category": item["category"],
            }
        )
    return out


def disease_items(disease) -> list[dict]:
    return _unique_keyed_items(_normalize_items(disease.checklist_items() or []))


def catalog_items() -> list[dict]:
    rows = SymptomCatalog.query.order_by(SymptomCatalog.category.asc(), SymptomCatalog.label.asc()).all()
    return _unique_keyed_items(
        _normalize_items(
            [
                {"key": f"catalog_{row.id}", "label": row.label, "category": row.category}
                | {"label_km": row.label_km or row.label}
                for row in rows
            ]
        )
    )


def ensure_catalog_symptom(
    *,
    label: str,
    label_km: str | None = None,
    category: str,
    user_id: int | None = None,
) -> tuple[SymptomCatalog, bool]:
    clean_label = (label or "").strip()
    clean_label_km = (label_km or "").strip() or clean_label
    clean_category = canonical_category(category)
    if not clean_label:
        raise ValueError("Symptom label is required")

    existing = (
        SymptomCatalog.query.filter(
            db.func.lower(SymptomCatalog.label) == clean_label.lower(),
            db.func.lower(SymptomCatalog.category) == clean_category.lower(),
        )
        .order_by(SymptomCatalog.id.asc())
        .first()
    )
    if existing:
        changed = False
        if existing.label_km != clean_label_km:
            existing.label_km = clean_label_km
            changed = True
        if user_id and (existing.updated_by_id is None or changed):
            existing.updated_by_id = user_id
            existing.updated_at = datetime.utcnow()
        return existing, False

    symptom = SymptomCatalog(
        label=clean_label,
        label_km=clean_label_km,
        category=clean_category,
        created_by_id=user_id,
        updated_by_id=user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.session.add(symptom)
    db.session.flush()
    return symptom, True


def edit_catalog_symptom(
    *,
    old_label: str,
    old_category: str,
    new_label: str,
    new_label_km: str | None = None,
    new_category: str,
    user_id: int | None = None,
) -> int:
    source_label = (old_label or "").strip().lower()
    source_category = canonical_category(old_category).lower()
    target_label = (new_label or "").strip()
    target_label_km = (new_label_km or "").strip() or target_label
    target_category = canonical_category(new_category)
    if not source_label or not target_label:
        return 0

    matches = (
        SymptomCatalog.query.filter(
            db.func.lower(SymptomCatalog.label) == source_label,
            db.func.lower(SymptomCatalog.category) == source_category,
        )
        .order_by(SymptomCatalog.id.asc())
        .all()
    )

    for row in matches:
        row.label = target_label
        row.label_km = target_label_km
        row.category = target_category
        row.updated_by_id = user_id
        row.updated_at = datetime.utcnow()

    return len(matches)


def delete_catalog_symptom(*, label: str, category: str) -> int:
    clean_label = (label or "").strip().lower()
    clean_category = canonical_category(category).lower()
    if not clean_label:
        return 0

    matches = (
        SymptomCatalog.query.filter(
            db.func.lower(SymptomCatalog.label) == clean_label,
            db.func.lower(SymptomCatalog.category) == clean_category,
        )
        .order_by(SymptomCatalog.id.asc())
        .all()
    )
    removed = len(matches)
    for row in matches:
        db.session.delete(row)
    return removed


def ordered_checklist_groups(items: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for item in _unique_keyed_items(_normalize_items(items)):
        category = canonical_category(item.get("category") or DEFAULT_CATEGORY)
        grouped.setdefault(category, []).append(item)

    ordered_names = [label for label, _ in CHECKLIST_CATEGORY_CHOICES]
    groups: list[dict] = []

    for category in ordered_names:
        rows = grouped.pop(category, [])
        groups.append(
            {
                "category": category,
                "count": len(rows),
                "items": sorted(rows, key=lambda row: (row.get("label") or "").lower()),
            }
        )

    for category in sorted(grouped.keys(), key=lambda value: value.lower()):
        rows = grouped[category]
        groups.append(
            {
                "category": category,
                "count": len(rows),
                "items": sorted(rows, key=lambda row: (row.get("label") or "").lower()),
            }
        )

    return groups


def checklist_to_symptoms_text(items: list[dict]) -> str:
    return checklist_to_symptoms_text_for_lang(items, "en")


def checklist_to_symptoms_text_for_lang(items: list[dict], lang: str = "en") -> str:
    normalized = _unique_keyed_items(_normalize_items(items))
    lines: list[str] = []
    for item in normalized:
        label = (
            (item.get("label_km") if lang == "km" else item.get("label"))
            or item.get("label")
            or ""
        ).strip()
        category = canonical_category(item.get("category") or SYNC_DEFAULT_CATEGORY)
        if not label:
            continue
        if _norm(category) == _norm(DEFAULT_CATEGORY):
            category = SYNC_DEFAULT_CATEGORY
        lines.append(f"{category}: {label}")
    return "\n".join(lines)


def parse_symptoms_text_to_items(
    text: str,
    *,
    default_category: str = SYNC_DEFAULT_CATEGORY,
) -> list[dict]:
    rows: list[dict] = []
    seen_pairs: set[tuple[str, str]] = set()

    for raw in (text or "").splitlines():
        line = str(raw or "").strip()
        if not line:
            continue
        line = re.sub(r"^[-*•\s]+", "", line).strip()
        if not line:
            continue

        category = default_category
        label = line
        if ":" in line:
            left, right = line.split(":", 1)
            left = (left or "").strip()
            right = (right or "").strip()
            if right:
                label = right
                category = canonical_category(left or default_category)

        category = canonical_category(category or default_category)
        if _norm(category) == _norm(DEFAULT_CATEGORY):
            category = default_category

        label = (label or "").strip()
        if not label:
            continue

        pair = (_norm(category), _norm(label))
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        rows.append({"key": keyify(label), "label": label, "label_km": label, "category": category})

    if not rows and (text or "").strip():
        # Keep a non-empty fallback so symptoms text and checklist never diverge.
        fallback = re.sub(r"\s+", " ", (text or "").strip())
        if fallback:
            cat = canonical_category(default_category or SYNC_DEFAULT_CATEGORY)
            rows.append({"key": keyify(fallback), "label": fallback, "label_km": fallback, "category": cat})

    return _unique_keyed_items(_normalize_items(rows))


def save_disease_items(disease, items: list[dict]) -> None:
    normalized_raw = _unique_keyed_items(_normalize_items(items))
    normalized: list[dict] = []
    for item in normalized_raw:
        label = (item.get("label") or "").strip()
        label_km = (item.get("label_km") or "").strip() or label
        key = (item.get("key") or "").strip() or keyify(label)
        category = canonical_category(item.get("category") or SYNC_DEFAULT_CATEGORY)
        if _norm(category) == _norm(DEFAULT_CATEGORY):
            category = SYNC_DEFAULT_CATEGORY
        if not label:
            continue
        normalized.append({"key": key, "label": label, "label_km": label_km, "category": category})

    disease.symptom_checklist_json = json.dumps(normalized)
    disease.symptoms = checklist_to_symptoms_text_for_lang(normalized, "en")
    disease.symptoms_km = checklist_to_symptoms_text_for_lang(normalized, "km")


def sync_disease_symptom_data(disease) -> bool:
    old_json = disease.symptom_checklist_json or ""
    old_symptoms = disease.symptoms or ""

    existing = disease_items(disease)
    if existing:
        save_disease_items(disease, existing)
        return (disease.symptom_checklist_json or "") != old_json or (
            disease.symptoms or ""
        ) != old_symptoms

    parsed = parse_symptoms_text_to_items(disease.symptoms or "")
    if not parsed:
        return False
    save_disease_items(disease, parsed)
    return (disease.symptom_checklist_json or "") != old_json or (disease.symptoms or "") != old_symptoms


def add_symptom_to_disease(disease, *, label: str, label_km: str | None = None, category: str) -> bool:
    label = (label or "").strip()
    if not label:
        return False

    items = disease_items(disease)
    cat = canonical_category(category)
    pair = (_norm(cat), _norm(label))
    if any((_norm(it["category"]), _norm(it["label"])) == pair for it in items):
        return False

    items.append(
        {
            "key": keyify(label),
            "label": label,
            "label_km": (label_km or "").strip() or label,
            "category": cat,
        }
    )
    save_disease_items(disease, items)
    return True


def remove_symptom_from_disease(disease, *, label: str, category: str) -> bool:
    target = (_norm(canonical_category(category)), _norm(label))
    items = disease_items(disease)
    kept = [
        item
        for item in items
        if (_norm(item.get("category")), _norm(item.get("label"))) != target
    ]
    if len(kept) == len(items):
        return False
    save_disease_items(disease, kept)
    return True


def edit_symptom_globally(
    diseases: list,
    *,
    old_label: str,
    old_category: str,
    new_label: str,
    new_label_km: str | None = None,
    new_category: str,
) -> tuple[int, int, set[int]]:
    old_pair = (_norm(canonical_category(old_category)), _norm(old_label))
    new_label = (new_label or "").strip()
    new_label_km = (new_label_km or "").strip() or new_label
    new_cat = canonical_category(new_category)
    if not new_label:
        return (0, 0, set())

    affected_diseases = 0
    affected_items = 0
    changed_disease_ids: set[int] = set()

    for disease in diseases:
        items = disease_items(disease)
        changed = False
        for item in items:
            pair = (_norm(item.get("category")), _norm(item.get("label")))
            if pair == old_pair:
                item["label"] = new_label
                item["label_km"] = new_label_km
                item["category"] = new_cat
                item["key"] = keyify(new_label)
                affected_items += 1
                changed = True

        if changed:
            save_disease_items(disease, items)
            affected_diseases += 1
            changed_disease_ids.add(disease.id)

    return (affected_diseases, affected_items, changed_disease_ids)


def sync_all_disease_symptom_data(diseases: list) -> bool:
    changed = False
    for disease in diseases:
        if sync_disease_symptom_data(disease):
            changed = True
    return changed


def delete_symptom_globally(
    diseases: list,
    *,
    label: str,
    category: str,
) -> tuple[int, int, set[int]]:
    target = (_norm(canonical_category(category)), _norm(label))
    affected_diseases = 0
    removed_items = 0
    changed_disease_ids: set[int] = set()

    for disease in diseases:
        items = disease_items(disease)
        kept = []
        removed_here = 0
        for item in items:
            pair = (_norm(item.get("category")), _norm(item.get("label")))
            if pair == target:
                removed_here += 1
            else:
                kept.append(item)

        if removed_here:
            save_disease_items(disease, kept)
            affected_diseases += 1
            removed_items += removed_here
            changed_disease_ids.add(disease.id)

    return (affected_diseases, removed_items, changed_disease_ids)


def collect_all_symptoms(diseases: list) -> list[dict]:
    symptom_map: dict[tuple[str, str], dict] = {}

    for disease in diseases:
        for item in disease_items(disease):
            label = (item.get("label") or "").strip()
            category = canonical_category(item.get("category") or DEFAULT_CATEGORY)
            if not label:
                continue

            map_key = (_norm(category), _norm(label))
            if map_key not in symptom_map:
                symptom_map[map_key] = {
                    "category": category,
                    "label": label,
                    "label_km": (item.get("label_km") or label).strip() or label,
                    "disease_ids": set(),
                    "disease_names": set(),
                }
            elif not symptom_map[map_key].get("label_km"):
                symptom_map[map_key]["label_km"] = (item.get("label_km") or label).strip() or label

            symptom_map[map_key]["disease_ids"].add(disease.id)
            symptom_map[map_key]["disease_names"].add(disease.name)

    for item in catalog_items():
        label = (item.get("label") or "").strip()
        category = canonical_category(item.get("category") or DEFAULT_CATEGORY)
        if not label:
            continue

        map_key = (_norm(category), _norm(label))
        if map_key not in symptom_map:
            symptom_map[map_key] = {
                "category": category,
                "label": label,
                "label_km": (item.get("label_km") or label).strip() or label,
                "disease_ids": set(),
                "disease_names": set(),
            }

    return sorted(
        (
            {
                "category": row["category"],
                "label": row["label"],
                "label_km": row["label_km"],
                "disease_count": len(row["disease_ids"]),
                "disease_ids": sorted(row["disease_ids"]),
                "disease_names": sorted(row["disease_names"]),
            }
            for row in symptom_map.values()
        ),
        key=lambda row: (row["category"].lower(), row["label"].lower()),
    )
