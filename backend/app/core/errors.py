"""Application error hierarchy and FastAPI exception handlers.

Every error renders as application/problem+json:
  { type, title, status, detail, errors: [{ field, message }] }

This matches the contract in docs/ARCHITECTURE.md § Conventions.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------------
# Error hierarchy
# ---------------------------------------------------------------------------


class AppError(Exception):
    """Base for all application-level errors.

    Subclass this, set ``status`` and ``title``, and raise. The exception
    handler below converts it to a problem+json response.
    """

    status: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    title: str = "Internal Server Error"
    type_uri: str = "about:blank"

    def __init__(
        self,
        detail: str = "",
        errors: Sequence[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.errors: list[dict[str, Any]] = list(errors) if errors else []


class NotFoundError(AppError):
    status = status.HTTP_404_NOT_FOUND
    title = "Not Found"
    type_uri = "/errors/not-found"


class ConflictError(AppError):
    status = status.HTTP_409_CONFLICT
    title = "Conflict"
    type_uri = "/errors/conflict"


class ForbiddenError(AppError):
    status = status.HTTP_403_FORBIDDEN
    title = "Forbidden"
    type_uri = "/errors/forbidden"


class UnauthorizedError(AppError):
    status = status.HTTP_401_UNAUTHORIZED
    title = "Unauthorized"
    type_uri = "/errors/unauthorized"


class ValidationFailedError(AppError):
    status = status.HTTP_422_UNPROCESSABLE_CONTENT
    title = "Validation Failed"
    type_uri = "/errors/validation-failed"


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


def _problem_response(
    status_code: int,
    type_uri: str,
    title: str,
    detail: str,
    errors: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {
        "type": type_uri,
        "title": title,
        "status": status_code,
        "detail": detail,
        "errors": errors or [],
    }
    return JSONResponse(
        content=body,
        status_code=status_code,
        media_type="application/problem+json",
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Render AppError subclasses as application/problem+json."""
    return _problem_response(
        status_code=exc.status,
        type_uri=exc.type_uri,
        title=exc.title,
        detail=exc.detail,
        errors=exc.errors,
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Convert Pydantic RequestValidationError to application/problem+json.

    Each Pydantic error becomes one entry in errors[]:
      { "field": "body.email", "message": "value is not a valid email address" }
    """
    errors = [
        {
            "field": ".".join(str(loc) for loc in err["loc"]),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return _problem_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        type_uri="/errors/validation-failed",
        title="Validation Failed",
        detail="One or more fields failed validation.",
        errors=errors,
    )
