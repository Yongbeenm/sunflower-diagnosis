"""Authentication and authorization models (User, Role, Permission)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.diagnosis import DiagnosisSession
    from app.models.feedback import Feedback


class RolePermission(Base):
    """Many-to-many join table connecting roles and permissions."""

    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Permission(Base):
    """Atomic authorization capability string (e.g. disease:create)."""

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="raise",
    )


class Role(Base):
    """Named collection of permissions assigned to users."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    permissions: Mapped[list[Permission]] = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="raise",
    )
    users: Mapped[list[User]] = relationship(
        "User",
        back_populates="role",
        lazy="raise",
    )


class User(Base, TimestampMixin):
    """Registered application user account."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    role: Mapped[Role] = relationship("Role", back_populates="users", lazy="raise")
    diagnosis_sessions: Mapped[list[DiagnosisSession]] = relationship(
        "DiagnosisSession",
        back_populates="user",
        lazy="raise",
    )
    feedback: Mapped[list[Feedback]] = relationship(
        "Feedback",
        back_populates="user",
        lazy="raise",
    )

    def has_permission(self, code: str) -> bool:
        """Check if user's role has been granted the given permission code."""
        if self.role is None:
            return False
        if self.role.name == "admin":
            return True
        return any(p.code == code for p in self.role.permissions)
