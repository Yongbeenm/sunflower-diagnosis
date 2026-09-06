from __future__ import annotations

from datetime import datetime

from extensions import db


class _I18nMessageMixin:
    __tablename__ = "i18n_messages"

    namespace = db.Column(db.String(32), primary_key=True)
    msg_key_hash = db.Column(db.String(64), primary_key=True)
    msg_key = db.Column(db.Text, nullable=False)
    msg_text = db.Column(db.Text, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class I18nMessageEN(_I18nMessageMixin, db.Model):
    __bind_key__ = "i18n_en"


class I18nMessageKM(_I18nMessageMixin, db.Model):
    __bind_key__ = "i18n_km"
