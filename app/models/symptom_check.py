"""Models to store Symptom Checker usage.

We keep a history of:
1) Each symptom check event (who/when + top result)
2) Which symptoms were selected
3) The ranked diagnosis results returned by the rule engine

This data helps admins understand common symptom patterns and improve the system.
"""

from __future__ import annotations

from datetime import datetime

from extensions import db


class SymptomCheck(db.Model):
    __tablename__ = "symptom_checks"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    selected_count = db.Column(db.Integer, nullable=False, default=0)

    # Top-ranked result (may be null if no diagnosis matched the threshold)
    top_disease_slug = db.Column(db.String(80), nullable=True, index=True)
    top_disease_name = db.Column(db.String(120), nullable=True)
    top_score = db.Column(db.Float, nullable=True)
    top_percent = db.Column(db.Integer, nullable=True)

    user = db.relationship("User", back_populates="symptom_checks")
    symptoms = db.relationship(
        "SymptomCheckSymptom",
        back_populates="check",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    results = db.relationship(
        "SymptomCheckResult",
        back_populates="check",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="SymptomCheckResult.rank.asc()",
    )

    def __repr__(self) -> str:
        return f"<SymptomCheck {self.id} user={self.user_id}>"


class SymptomCheckSymptom(db.Model):
    __tablename__ = "symptom_check_symptoms"

    id = db.Column(db.Integer, primary_key=True)
    check_id = db.Column(
        db.Integer, db.ForeignKey("symptom_checks.id"), nullable=False, index=True
    )

    symptom_key = db.Column(db.String(80), nullable=False, index=True)
    symptom_label = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(80), nullable=True)

    check = db.relationship("SymptomCheck", back_populates="symptoms")

    __table_args__ = (
        db.UniqueConstraint("check_id", "symptom_key", name="uq_check_symptom"),
    )

    def __repr__(self) -> str:
        return f"<SymptomCheckSymptom check={self.check_id} key={self.symptom_key}>"


class SymptomCheckResult(db.Model):
    __tablename__ = "symptom_check_results"

    id = db.Column(db.Integer, primary_key=True)
    check_id = db.Column(
        db.Integer, db.ForeignKey("symptom_checks.id"), nullable=False, index=True
    )

    rank = db.Column(db.Integer, nullable=False, default=1)
    disease_key = db.Column(db.String(80), nullable=False, index=True)
    disease_name = db.Column(db.String(120), nullable=False)

    # Option A (requested): real FK link to diseases.id
    # Keep disease_key/name as snapshots so history still displays even if a disease is renamed.
    disease_id = db.Column(
        db.Integer, db.ForeignKey("diseases.id", ondelete="SET NULL"), nullable=True, index=True
    )
    score = db.Column(db.Float, nullable=False)
    percent = db.Column(db.Integer, nullable=False)

    # JSON string of matched symptoms for this result: [(label, weight), ...]
    matched_json = db.Column(db.Text, nullable=True)

    check = db.relationship("SymptomCheck", back_populates="results")
    disease = db.relationship("Disease", lazy="joined")

    def __repr__(self) -> str:
        return f"<SymptomCheckResult check={self.check_id} rank={self.rank} disease={self.disease_key}>"
