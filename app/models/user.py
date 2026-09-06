from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin
from sqlalchemy.exc import OperationalError
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, login_manager

from app.models.rbac import Permission, Role, role_permissions


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # "user", "doctor", or "admin"
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # New: real FK connection to roles (optional; keeps legacy `role` string too)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=True, index=True)
    role_obj = db.relationship("Role", lazy="joined")

    symptom_checks = db.relationship(
        "SymptomCheck", back_populates="user", cascade="all, delete-orphan"
    )
    feedback_items = db.relationship(
        "Feedback", back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def has_permission(self, permission_name: str) -> bool:
        """Return True if this user's role has the named permission.

        Note: The app keeps `users.role` as a string for backwards compatibility
        and looks up Role by `Role.name == users.role`.
        """
        if not permission_name:
            return False

        # Fast path: keep legacy behaviour working even if RBAC tables are missing.
        if self.role == "admin" and permission_name == "access_admin":
            return True

        try:
            q = (
                db.session.query(Permission.id)
                .join(role_permissions, Permission.id == role_permissions.c.permission_id)
                .filter(Permission.name == permission_name)
            )

            # Prefer FK-based role connection when available.
            if self.role_id:
                q = q.filter(role_permissions.c.role_id == self.role_id)
            else:
                # Fallback to legacy string role mapping.
                q = q.join(Role, Role.id == role_permissions.c.role_id).filter(Role.name == self.role)

            row = q.first()
            return row is not None
        except OperationalError:
            # Database not fully initialized yet.
            return self.role == "admin"

    @property
    def is_admin(self) -> bool:
        # Prefer permission-based check, but keep compatibility with legacy role string.
        return (self.role_obj and self.role_obj.name == "admin") or self.role == "admin" or self.has_permission("access_admin")

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))
