"""Admin schemas for user and role management."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# ============================================================================
# User Management Schemas
# ============================================================================

class UserResponse(BaseModel):
    """User account information for admin view."""
    
    id: int
    username: str
    email: str
    role: str
    role_id: int
    is_active: bool
    created_at: datetime


class PaginatedUsersResponse(BaseModel):
    """Paginated list of users."""
    
    items: list[UserResponse]
    total: int
    page: int
    size: int


class UpdateUserRequest(BaseModel):
    """Request to update user account."""
    
    role_id: int | None = None
    is_active: bool | None = None


# ============================================================================
# Role & Permission Schemas
# ============================================================================

class RoleResponse(BaseModel):
    """Role information."""
    
    id: int
    name: str
    description: str | None = None
    permissions: list[str] = Field(default_factory=list)


class RoleListResponse(BaseModel):
    """All roles with full permission list."""
    
    items: list[RoleResponse]
    permissions: list[PermissionDetail]


class PermissionDetail(BaseModel):
    """Permission with granted status."""
    
    code: str
    description: str
    granted: bool


class RolePermissionsResponse(BaseModel):
    """Role with all permissions and their grant status."""
    
    role_id: int
    role_name: str
    permissions: list[PermissionDetail]


class RolePermissionsRequest(BaseModel):
    """Request to update role permissions."""
    
    permission_codes: list[str] = Field(default_factory=list)


# ============================================================================
# Ruleset Schemas
# ============================================================================

class RulesetResponse(BaseModel):
    """Diagnostic ruleset version."""
    
    id: int
    version: str
    algorithm: str
    parameters: dict
    is_active: bool
    published_at: datetime | None = None
    published_by: str | None = None


class RulesetActivateRequest(BaseModel):
    """Request to activate a ruleset (no body needed, just the endpoint)."""
    
    pass
