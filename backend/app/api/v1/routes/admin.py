"""Admin API routes for user and role management."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_permission
from app.models.auth import User
from app.repositories.admin import AdminRepository
from app.schemas.admin import (
    PaginatedUsersResponse,
    RolePermissionsRequest,
    RolePermissionsResponse,
    RulesetResponse,
    UpdateUserRequest,
    UserResponse,
)

router = APIRouter(prefix="/admin", tags=["admin"])


# ============================================================================
# User Management
# ============================================================================

@router.get(
    "/users",
    response_model=PaginatedUsersResponse,
    summary="List all user accounts",
)
async def list_users(
    current_user: Annotated[User, Depends(require_permission("user:manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    size: int = 20,
) -> PaginatedUsersResponse:
    """List all user accounts with pagination (admin only)."""
    repo = AdminRepository(db)
    users, total = await repo.list_users(page, size)
    
    return PaginatedUsersResponse(
        items=[
            UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role.name if user.role else "unknown",
                role_id=user.role_id,
                is_active=user.is_active,
                created_at=user.created_at,
            )
            for user in users
        ],
        total=total,
        page=page,
        size=size,
    )


@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Update user role or active status",
)
async def update_user(
    user_id: int,
    request: UpdateUserRequest,
    current_user: Annotated[User, Depends(require_permission("user:manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Update user's role or active status (admin only)."""
    repo = AdminRepository(db)
    
    user = await repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id and request.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )
    
    updated_user = await repo.update_user(
        user=user,
        role_id=request.role_id,
        is_active=request.is_active,
    )
    await db.commit()
    
    return UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        role=updated_user.role.name if updated_user.role else "unknown",
        role_id=updated_user.role_id,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at,
    )


# ============================================================================
# Role & Permission Management
# ============================================================================

@router.get(
    "/roles",
    summary="List all roles with permissions",
)
async def list_roles(
    current_user: Annotated[User, Depends(require_permission("rbac:manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all roles with full permission matrix (admin only)."""
    repo = AdminRepository(db)
    roles = await repo.get_roles()
    all_permissions = await repo.get_permissions()
    
    return {
        "items": [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": [p.code for p in role.permissions],
            }
            for role in roles
        ],
        "permissions": [
            {
                "id": p.id,
                "code": p.code,
                "description": p.description or "",
                "granted": False,  # This will be set per role in the items above
            }
            for p in all_permissions
        ],
    }


@router.get(
    "/roles/{role_id}/permissions",
    response_model=RolePermissionsResponse,
    summary="Get role permissions",
)
async def get_role_permissions(
    role_id: int,
    current_user: Annotated[User, Depends(require_permission("rbac:manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RolePermissionsResponse:
    """Get all permissions for a role with full permission list (admin only)."""
    repo = AdminRepository(db)
    
    role = await repo.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found",
        )
    
    all_permissions = await repo.get_permissions()
    role_permission_codes = {p.code for p in role.permissions}
    
    return RolePermissionsResponse(
        role_id=role.id,
        role_name=role.name,
        permissions=[
            {
                "code": p.code,
                "description": p.description or "",
                "granted": p.code in role_permission_codes,
            }
            for p in all_permissions
        ],
    )


@router.put(
    "/roles/{role_id}/permissions",
    response_model=RolePermissionsResponse,
    summary="Update role permissions",
)
async def update_role_permissions(
    role_id: int,
    request: RolePermissionsRequest,
    current_user: Annotated[User, Depends(require_permission("rbac:manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RolePermissionsResponse:
    """Update permissions for a role (admin only)."""
    repo = AdminRepository(db)
    
    role = await repo.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found",
        )
    
    updated_role = await repo.set_role_permissions(role_id, request.permission_codes)
    await db.commit()
    
    all_permissions = await repo.get_permissions()
    role_permission_codes = {p.code for p in updated_role.permissions}
    
    return RolePermissionsResponse(
        role_id=updated_role.id,
        role_name=updated_role.name,
        permissions=[
            {
                "code": p.code,
                "description": p.description or "",
                "granted": p.code in role_permission_codes,
            }
            for p in all_permissions
        ],
    )


# ============================================================================
# Ruleset Management
# ============================================================================

@router.get(
    "/rulesets",
    response_model=list[RulesetResponse],
    summary="List all rulesets",
)
async def list_rulesets(
    current_user: Annotated[User, Depends(require_permission("ruleset:manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[RulesetResponse]:
    """List all diagnostic rulesets (admin only)."""
    repo = AdminRepository(db)
    rulesets = await repo.list_rulesets()
    
    return [
        RulesetResponse(
            id=ruleset.id,
            version=ruleset.version,
            algorithm=ruleset.algorithm,
            parameters=ruleset.params,
            is_active=ruleset.is_active,
            published_at=ruleset.published_at,
            published_by=ruleset.published_by.username if ruleset.published_by else None,
        )
        for ruleset in rulesets
    ]


@router.post(
    "/rulesets/{ruleset_id}/activate",
    response_model=RulesetResponse,
    summary="Activate a ruleset version",
)
async def activate_ruleset(
    ruleset_id: int,
    current_user: Annotated[User, Depends(require_permission("ruleset:manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RulesetResponse:
    """Activate a specific ruleset version (admin only).
    
    This will deactivate all other rulesets and make this one active.
    """
    repo = AdminRepository(db)
    
    ruleset = await repo.get_ruleset_by_id(ruleset_id)
    if not ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ruleset with ID {ruleset_id} not found",
        )
    
    activated_ruleset = await repo.activate_ruleset(ruleset_id, current_user.id)
    await db.commit()
    
    return RulesetResponse(
        id=activated_ruleset.id,
        version=activated_ruleset.version,
        algorithm=activated_ruleset.algorithm,
        parameters=activated_ruleset.params,
        is_active=activated_ruleset.is_active,
        published_at=activated_ruleset.published_at,
        published_by=activated_ruleset.published_by.username if activated_ruleset.published_by else None,
    )
