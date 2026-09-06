from __future__ import annotations

from datetime import datetime

from extensions import db


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    symptom_check_id = db.Column(
        db.Integer, db.ForeignKey("symptom_checks.id"), nullable=True, index=True
    )
    subject = db.Column(db.String(160), nullable=False)
    message = db.Column(db.Text, nullable=False)
    photo_filename = db.Column(db.String(220), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="open", index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship("User", back_populates="feedback_items")
    symptom_check = db.relationship("SymptomCheck", lazy="joined")

    def __repr__(self) -> str:
        return f"<Feedback {self.id} user={self.user_id} status={self.status}>"
