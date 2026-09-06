from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict

from flask import current_app
from extensions import db

from app.models.i18n_message import I18nMessageEN, I18nMessageKM

def _hash_key(value: str) -> str:
    return hashlib.sha256((value or "").encode("utf-8")).hexdigest()

def _model_for_lang(lang: str):
    return I18nMessageKM if lang == "km" else I18nMessageEN


def _seed_path(filename: str) -> Path:
    base_dir = Path(current_app.root_path).resolve()
    return base_dir / "i18n_seed" / filename


def _load_seed_file(filename: str) -> dict[str, str]:
    p = _seed_path(filename)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}

    clean: dict[str, str] = {}
    for k, v in data.items():
        key = str(k or "").strip()
        if not key:
            continue
        clean[key] = str(v or "")
    return clean


def _seed_namespace(model_cls, namespace: str, values: dict[str, str]) -> None:
    if not values:
        return

    existing_rows = {
        str(row.msg_key_hash): row
        for row in model_cls.query.filter_by(namespace=namespace).all()
    }

    for key, text in values.items():
        key_hash = _hash_key(key)
        row = existing_rows.get(key_hash)
        if row is None:
            row = model_cls(
                namespace=namespace,
                msg_key_hash=key_hash,
                msg_key=key,
                msg_text=text,
            )
            db.session.add(row)
            existing_rows[key_hash] = row
        else:
            row.msg_key = key
            row.msg_text = text


def init_i18n_databases() -> None:
    """Create and seed i18n databases through SQLAlchemy binds."""
    db.create_all(bind_key=["i18n_en", "i18n_km"])

    seed_map = {
        "en": {
            "ui": _load_seed_file("en_ui.json"),
            "phrases": _load_seed_file("en_phrases.json"),
        },
        "km": {
            "ui": _load_seed_file("km_ui.json"),
            "phrases": _load_seed_file("km_phrases.json"),
        },
    }

    _seed_namespace(I18nMessageEN, "ui", seed_map["en"]["ui"])
    _seed_namespace(I18nMessageEN, "phrases", seed_map["en"]["phrases"])
    _seed_namespace(I18nMessageKM, "ui", seed_map["km"]["ui"])
    _seed_namespace(I18nMessageKM, "phrases", seed_map["km"]["phrases"])
    db.session.commit()


def _read_namespace(lang: str, namespace: str) -> dict[str, str]:
    model_cls = _model_for_lang(lang)
    rows = model_cls.query.filter_by(namespace=namespace).all()
    return {str(row.msg_key): str(row.msg_text) for row in rows}


def load_i18n_store() -> dict[str, dict[str, Dict[str, str]]]:
    """Return both language catalogs for frontend usage."""
    return {
        "en": {
            "ui": _read_namespace("en", "ui"),
            "phrases": _read_namespace("en", "phrases"),
        },
        "km": {
            "ui": _read_namespace("km", "ui"),
            "phrases": _read_namespace("km", "phrases"),
        },
    }
