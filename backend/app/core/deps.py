"""Dependencies for authentication and authorization."""
from typing import Optional, List, Callable
from functools import wraps
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.user import User, UserProfile
from app.models.admin import UserRole
from app.core.security import decode_token

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise None.
    Use this for endpoints that work with or without authentication.
    """
    if not credentials:
        return None

    payload = decode_token(credentials.credentials)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    query = (
        select(User)
        .where(User.id == int(user_id), User.is_active == True)
        .options(selectinload(User.profile))
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user (required).
    Raises 401 if not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    query = (
        select(User)
        .where(User.id == int(user_id), User.is_active == True)
        .options(selectinload(User.profile))
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    """
    Get current user's profile.
    Assumes user is authenticated.
    """
    if user.profile:
        return user.profile

    # If profile not loaded, fetch it
    query = select(UserProfile).where(UserProfile.user_id == user.id)
    result = await db.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    return profile


# =============================================================================
# Admin Authentication Dependencies
# =============================================================================

# Role hierarchy: super_admin > admin > moderator > user
ROLE_HIERARCHY = {
    UserRole.USER: 0,
    UserRole.MODERATOR: 1,
    UserRole.ADMIN: 2,
    UserRole.SUPER_ADMIN: 3,
}


def has_role_level(user_role: UserRole, required_role: UserRole) -> bool:
    """Check if user has at least the required role level."""
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify they are not banned.
    """
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been banned",
        )
    return user


async def get_current_moderator(
    user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user if they have at least moderator role.
    Raises 403 if user doesn't have sufficient permissions.
    """
    if not has_role_level(user.role, UserRole.MODERATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator access required",
        )
    return user


async def get_current_admin(
    user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user if they have at least admin role.
    Raises 403 if user doesn't have sufficient permissions.
    """
    if not has_role_level(user.role, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


async def get_current_super_admin(
    user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user if they have super admin role.
    Raises 403 if user doesn't have sufficient permissions.
    """
    if user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )
    return user


class RequireRole:
    """
    Dependency class to require specific roles.

    Usage:
        @router.get("/admin/users")
        async def list_users(user: User = Depends(RequireRole(UserRole.ADMIN))):
            ...
    """

    def __init__(self, min_role: UserRole):
        self.min_role = min_role

    async def __call__(
        self,
        user: User = Depends(get_current_active_user),
    ) -> User:
        if not has_role_level(user.role, self.min_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{self.min_role.value.replace('_', ' ').title()} access required",
            )
        return user


class RequireRoles:
    """
    Dependency class to require any of specific roles.

    Usage:
        @router.get("/admin/content")
        async def manage_content(user: User = Depends(RequireRoles([UserRole.MODERATOR, UserRole.ADMIN]))):
            ...
    """

    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        user: User = Depends(get_current_active_user),
    ) -> User:
        if user.role not in self.allowed_roles:
            role_names = ", ".join([r.value for r in self.allowed_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these roles required: {role_names}",
            )
        return user


# Convenience dependencies for common use cases
require_moderator = RequireRole(UserRole.MODERATOR)
require_admin = RequireRole(UserRole.ADMIN)
require_super_admin = RequireRole(UserRole.SUPER_ADMIN)
