import os
import re

from werkzeug.utils import secure_filename

_LEAF_CATEGORY = "Leaf"
_LEAF_HEAD_CATEGORY = "Leaf / Head"
_WHOLE_PLANT_CATEGORY = "Whole plant"
_STEM_CATEGORY = "Stem"
_HEAD_CATEGORY = "Head"
_ROOT_CATEGORY = "Root"
_SEEDLING_CATEGORY = "Seed / Seedling"
_ENV_CATEGORY = "Environment"


def _clean_lines(text: str) -> list[str]:
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


def _dedupe_key(key: str, seen: set[str]) -> str:
    base = key
    i = 1
    while key in seen:
        i += 1
        key = f"{base}_{i}"
    return key


def _normalize_category(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (label or "").strip().lower())


def build_checklist_from_sections(
    leaf_text: str,
    leaf_head_text: str,
    whole_plant_text: str,
    stem_text: str,
    head_text: str,
    root_text: str,
    environment_text: str,
    seedling_text: str = "",
) -> list[dict]:
    """Create checklist items from section inputs."""
    items: list[dict] = []
    seen: set[str] = set()

    def add_item(label: str, category: str) -> None:
        k = keyify(label)
        k = _dedupe_key(k, seen)
        seen.add(k)
        items.append({"key": k, "label": label, "category": category})

    for line in _clean_lines(leaf_text):
        add_item(line, _LEAF_CATEGORY)

    for line in _clean_lines(leaf_head_text):
        add_item(line, _LEAF_HEAD_CATEGORY)

    for line in _clean_lines(whole_plant_text):
        add_item(line, _WHOLE_PLANT_CATEGORY)

    for line in _clean_lines(stem_text):
        add_item(line, _STEM_CATEGORY)

    for line in _clean_lines(head_text):
        add_item(line, _HEAD_CATEGORY)

    for line in _clean_lines(root_text):
        add_item(line, _ROOT_CATEGORY)

    for line in _clean_lines(seedling_text):
        add_item(line, _SEEDLING_CATEGORY)

    env_lines = []
    for line in _clean_lines(environment_text):
        if ":" in line:
            env_lines.append(line)
        else:
            env_lines.append(f"{_ENV_CATEGORY}: {line}")

    env_items = parse_checklist("\n".join(env_lines))
    for it in env_items:
        label = (it.get("label") or "").strip()
        category = (it.get("category") or _ENV_CATEGORY).strip() or _ENV_CATEGORY
        if not label:
            continue
        add_item(label, category)

    return items


def split_checklist_sections(items: list[dict]) -> dict:
    """Split checklist items into section texts for UI."""
    leaf: list[str] = []
    leaf_head: list[str] = []
    whole_plant: list[str] = []
    stem: list[str] = []
    head: list[str] = []
    root: list[str] = []
    seedling: list[str] = []
    environment: list[str] = []

    for it in items or []:
        label = (it.get("label") or "").strip()
        if not label:
            continue
        category = (it.get("category") or "").strip()
        norm = _normalize_category(category)

        if norm == "leaf":
            leaf.append(label)
        elif norm == "leafhead":
            leaf_head.append(label)
        elif norm == "wholeplant":
            whole_plant.append(label)
        elif norm == "stem":
            stem.append(label)
        elif norm == "head":
            head.append(label)
        elif norm == "root":
            root.append(label)
        elif norm in {"seed", "seedling", "seedlings", "seedseedling"}:
            seedling.append(label)
        elif norm in {"environment", "env", "environmental"}:
            environment.append(label)
        else:
            if category:
                environment.append(f"{category}: {label}")
            else:
                environment.append(label)

    return {
        "leaf": "\n".join(leaf),
        "leaf_head": "\n".join(leaf_head),
        "whole_plant": "\n".join(whole_plant),
        "stem": "\n".join(stem),
        "head": "\n".join(head),
        "root": "\n".join(root),
        "seedling": "\n".join(seedling),
        "environment": "\n".join(environment),
    }


def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "report"


def unique_slug(model, base_slug: str, *, exclude_id: int | None = None) -> str:
    base_slug = (base_slug or "report")[:140]
    slug = base_slug
    i = 1
    while True:
        q = model.query.filter_by(slug=slug)
        if exclude_id is not None:
            q = q.filter(model.id != exclude_id)
        if not q.first():
            return slug
        i += 1
        suffix = f"-{i}"
        slug = f"{base_slug[: max(1, 140 - len(suffix))]}{suffix}"


def save_uploaded_image(file_storage, *, images_dir: str, filename_prefix: str) -> str | None:
    """Save an uploaded image into /static/images and return the stored filename."""

    if not file_storage:
        return None

    filename = secure_filename(file_storage.filename or "")
    if not filename:
        return None

    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
        raise ValueError("Image must be PNG/JPG/WEBP")

    os.makedirs(images_dir, exist_ok=True)
    stored = f"{filename_prefix}{ext}"
    save_path = os.path.join(images_dir, stored)
    file_storage.save(save_path)
    return stored


def keyify(label: str) -> str:
    v = (label or "").strip().lower()
    v = re.sub(r"[^a-z0-9]+", "_", v)
    v = re.sub(r"_{2,}", "_", v).strip("_")
    return v or "symptom"


def parse_checklist(text: str) -> list[dict]:
    """Parse checklist text into a JSON-serializable list of {key,label,category}.

    Each line can be:
      - "Category: Symptom label"
      - "Symptom label" (category becomes "General")
    """
    items: list[dict] = []
    seen: set[str] = set()
    for raw in (text or "").splitlines():
        line = (raw or "").strip()
        if not line:
            continue
        category = "General"
        label = line
        if ":" in line:
            left, right = line.split(":", 1)
            if right.strip():
                category = left.strip() or "General"
                label = right.strip()
        key = keyify(label)
        base = key
        i = 1
        while key in seen:
            i += 1
            key = f"{base}_{i}"
        seen.add(key)
        items.append({"key": key, "label": label, "category": category})
    return items
