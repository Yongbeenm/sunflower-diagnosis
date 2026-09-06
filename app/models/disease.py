import json
from datetime import datetime

from extensions import db


class Disease(db.Model):
    __tablename__ = "diseases"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    # English (legacy/default)
    name = db.Column(db.String(120), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    cause = db.Column(db.Text, nullable=False)
    treatment = db.Column(db.Text, nullable=False)
    prevention = db.Column(db.Text, nullable=False)
    # Khmer
    name_km = db.Column(db.String(120), nullable=True)
    symptoms_km = db.Column(db.Text, nullable=True)
    cause_km = db.Column(db.Text, nullable=True)
    treatment_km = db.Column(db.Text, nullable=True)
    prevention_km = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(200), nullable=True)

    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
    )

    # Symptom checklist stored directly on the disease (no extra tables).
    # JSON list, e.g. [{"key":"yellow_spots_leaves","label":"Yellow spots on leaves","category":"Leaf"}, ...]
    symptom_checklist_json = db.Column(db.Text, nullable=True, default="[]")

    created_by = db.relationship("User", foreign_keys=[created_by_id], lazy="joined")
    updated_by = db.relationship("User", foreign_keys=[updated_by_id], lazy="joined")

    def checklist_items(self) -> list[dict]:
        try:
            items = json.loads(self.symptom_checklist_json or "[]")
            return items if isinstance(items, list) else []
        except Exception:
            return []

    def _localized(self, field: str, lang: str = "en") -> str:
        if lang == "km":
            km_value = (getattr(self, f"{field}_km", None) or "").strip()
            if km_value:
                return km_value
        return (getattr(self, field, None) or "").strip()

    def display_name(self, lang: str = "en") -> str:
        return self._localized("name", lang)

    def display_symptoms(self, lang: str = "en") -> str:
        return self._localized("symptoms", lang)

    def display_cause(self, lang: str = "en") -> str:
        return self._localized("cause", lang)

    def display_treatment(self, lang: str = "en") -> str:
        return self._localized("treatment", lang)

    def display_prevention(self, lang: str = "en") -> str:
        return self._localized("prevention", lang)

    def __repr__(self):
        return f"<Disease {self.name}>"
