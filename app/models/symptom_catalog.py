from datetime import datetime

from extensions import db


class SymptomCatalog(db.Model):
    __tablename__ = "symptom_catalog"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(255), nullable=False, index=True)
    label_km = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(80), nullable=False, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=True,
    )

    created_by = db.relationship("User", foreign_keys=[created_by_id], lazy="joined")
    updated_by = db.relationship("User", foreign_keys=[updated_by_id], lazy="joined")

    def __repr__(self):
        return f"<SymptomCatalog {self.category}: {self.label}>"
