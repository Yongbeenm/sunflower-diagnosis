"""Admin service coordinating RBAC, user management, and ruleset operations."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationFailedError
from app.repositories.admin import AdminRepository
from app.schemas.admin import (
    AdminUserItem,
    AdminUserListResponse,
    AdminUserUpdateRequest,
    PermissionItem,
    RoleItem,
    RoleListResponse,
    RulesetActivateResponse,
    RulesetItem,
    RulesetListResponse,
    UpdateRolePermissionsRequest,
)


class AdminService:
    """Coordinates administrative operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = AdminRepository(session)

    # -----------------------------------------------------------------------
    # Roles & Permissions
    # -----------------------------------------------------------------------

    async def get_roles(self) -> RoleListResponse:
        """Fetch all roles and permission definitions."""
        roles = await self.repo.get_roles()
        permissions = await self.repo.get_permissions()

        role_items = [
            RoleItem(
                id=r.id,
                name=r.name,
                description=r.description,
                permissions=[p.code for p in r.permissions],
            )
            for r in roles
        ]

        permission_items = [
            PermissionItem(id=p.id, code=p.code, description=p.description) for p in permissions
        ]

        return RoleListResponse(items=role_items, permissions=permission_items)

    async def update_role_permissions(
        self,
        role_id: int,
        req: UpdateRolePermissionsRequest,
    ) -> RoleItem:
        """Replace permissions for a role."""
        role = await self.repo.get_role_by_id(role_id)
        if not role:
            raise NotFoundError(detail=f"Role #{role_id} not found")

        updated = await self.repo.set_role_permissions(role_id, req.permission_codes)
        return RoleItem(
            id=updated.id,
            name=updated.name,
            description=updated.description,
            permissions=[p.code for p in updated.permissions],
        )

    # -----------------------------------------------------------------------
    # Users
    # -----------------------------------------------------------------------

    async def list_users(self, page: int = 1, size: int = 20) -> AdminUserListResponse:
        """List users paginated."""
        users, total = await self.repo.list_users(page, size)
        items = [
            AdminUserItem(
                id=u.id,
                username=u.username,
                email=u.email,
                role=u.role.name if u.role else "unknown",
                role_id=u.role_id,
                is_active=u.is_active,
                created_at=u.created_at.isoformat(),
            )
            for u in users
        ]
        return AdminUserListResponse(items=items, total=total, page=page, size=size)

    async def update_user(
        self,
        user_id: int,
        req: AdminUserUpdateRequest,
    ) -> AdminUserItem:
        """Update a user's role assignment or active state."""
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise NotFoundError(detail=f"User #{user_id} not found")

        if req.role_id is not None:
            role = await self.repo.get_role_by_id(req.role_id)
            if not role:
                raise ValidationFailedError(detail=f"Role #{req.role_id} does not exist")

        updated = await self.repo.update_user(user, role_id=req.role_id, is_active=req.is_active)
        return AdminUserItem(
            id=updated.id,
            username=updated.username,
            email=updated.email,
            role=updated.role.name if updated.role else "unknown",
            role_id=updated.role_id,
            is_active=updated.is_active,
            created_at=updated.created_at.isoformat(),
        )

    # -----------------------------------------------------------------------
    # Rulesets
    # -----------------------------------------------------------------------

    async def list_rulesets(self) -> RulesetListResponse:
        """List all rulesets."""
        rulesets = await self.repo.list_rulesets()
        items = [
            RulesetItem(
                id=r.id,
                version=r.version,
                algorithm=r.algorithm,
                params=r.params,
                is_active=r.is_active,
                published_at=r.published_at.isoformat() if r.published_at else None,
                published_by=r.published_by.username if r.published_by else None,
            )
            for r in rulesets
        ]
        return RulesetListResponse(items=items)

    async def activate_ruleset(self, ruleset_id: int, user_id: int) -> RulesetActivateResponse:
        """Activate a ruleset."""
        ruleset = await self.repo.get_ruleset_by_id(ruleset_id)
        if not ruleset:
            raise NotFoundError(detail=f"Ruleset #{ruleset_id} not found")

        activated = await self.repo.activate_ruleset(ruleset_id, user_id)
        return RulesetActivateResponse(
            id=activated.id,
            version=activated.version,
            is_active=activated.is_active,
        )
