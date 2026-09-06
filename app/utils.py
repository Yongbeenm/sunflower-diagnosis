from __future__ import annotations

from functools import wraps

from flask import abort
from flask_login import current_user


def permission_required(permission_name: str):
    """Decorator: require a named permission on the current user."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if not getattr(current_user, "has_permission", None):
                abort(403)
            if not current_user.has_permission(permission_name):
                abort(403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
