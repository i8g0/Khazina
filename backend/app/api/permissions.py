"""Role and organization authorization dependencies (Sprint 4.3)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.api.deps import CurrentUserDep
from app.db.models import User
from app.db.models.enums import UserRole

ROLE_RANK: dict[UserRole, int] = {
    UserRole.ANALYST: 1,
    UserRole.EXECUTIVE: 2,
    UserRole.ADMIN: 3,
}


def _resolve_role(user: User) -> UserRole:
    try:
        return UserRole(user.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        ) from None


def _has_minimum_role(user: User, minimum_role: UserRole) -> bool:
    return ROLE_RANK[_resolve_role(user)] >= ROLE_RANK[minimum_role]


def require_role(minimum_role: UserRole):
    """Require an authenticated user with at least ``minimum_role``."""

    def dependency(current_user: CurrentUserDep) -> User:
        if not _has_minimum_role(current_user, minimum_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return current_user

    return dependency


def require_org_role(minimum_role: UserRole):
    """Require org membership and at least ``minimum_role`` for the path organization."""

    def dependency(organization_id: UUID, current_user: CurrentUserDep) -> User:
        if current_user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        if not _has_minimum_role(current_user, minimum_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return current_user

    return dependency


RequireAnalyst = Annotated[User, Depends(require_role(UserRole.ANALYST))]
RequireExecutive = Annotated[User, Depends(require_role(UserRole.EXECUTIVE))]
RequireAdmin = Annotated[User, Depends(require_role(UserRole.ADMIN))]

RequireOrgAnalyst = Annotated[User, Depends(require_org_role(UserRole.ANALYST))]
RequireOrgExecutive = Annotated[User, Depends(require_org_role(UserRole.EXECUTIVE))]
RequireOrgAdmin = Annotated[User, Depends(require_org_role(UserRole.ADMIN))]
