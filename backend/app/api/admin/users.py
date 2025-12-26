"""Admin user management API endpoints."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.user import User, UserProfile
from app.models.admin import UserRole, AuditLog
from app.core.deps import get_current_admin, get_current_super_admin, has_role_level
from app.schemas.admin import (
    UserRoleUpdate,
    UserBanRequest,
    AdminUserResponse,
    AdminUserListResponse,
)

router = APIRouter()


async def log_audit(
    db: AsyncSession,
    admin_id: int,
    action: str,
    entity_type: str,
    entity_id: int,
    old_values: dict = None,
    new_values: dict = None,
    request: Request = None,
):
    """Log an admin action."""
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    audit_log = AuditLog(
        admin_id=admin_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(audit_log)
    await db.flush()


@router.get("", response_model=AdminUserListResponse)
async def list_users(
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    is_banned: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern=r"^(email|name|created_at|last_login_at)$"),
    sort_order: str = Query("desc", pattern=r"^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """List all users with filtering and pagination."""
    # Build query
    query = select(User)
    count_query = select(func.count(User.id))

    # Apply filters
    filters = []
    if search:
        filters.append(or_(
            User.email.ilike(f"%{search}%"),
            User.name.ilike(f"%{search}%"),
        ))
    if role:
        filters.append(User.role == role)
    if is_active is not None:
        filters.append(User.is_active == is_active)
    if is_banned is not None:
        filters.append(User.is_banned == is_banned)

    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    # Get total count
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(User, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    users = [AdminUserResponse.model_validate(user) for user in result.scalars()]

    return AdminUserListResponse(
        items=users,
        total=total or 0,
        page=page,
        page_size=page_size,
    )


@router.get("/{user_id}", response_model=AdminUserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get a specific user."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return AdminUserResponse.model_validate(user)


@router.patch("/{user_id}/role")
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_super_admin),
):
    """Update a user's role. Requires super admin."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_role = user.role.value

    # Prevent creating super admins unless you're also a super admin
    if role_update.role == UserRole.SUPER_ADMIN and admin.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can create other super admins")

    user.role = role_update.role

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="change_user_role",
        entity_type="user",
        entity_id=user_id,
        old_values={"role": old_role},
        new_values={"role": role_update.role.value},
        request=request,
    )

    await db.commit()
    return {"message": "User role updated", "id": user_id, "role": role_update.role.value}


@router.patch("/{user_id}/ban")
async def ban_user(
    user_id: int,
    ban_request: UserBanRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Ban a user."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot ban yourself")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Cannot ban users with higher or equal role
    if has_role_level(user.role, admin.role):
        raise HTTPException(status_code=403, detail="Cannot ban a user with equal or higher role")

    if user.is_banned:
        raise HTTPException(status_code=400, detail="User is already banned")

    user.is_banned = True
    user.banned_reason = ban_request.reason
    user.banned_at = datetime.utcnow()
    user.banned_by_id = admin.id

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="ban_user",
        entity_type="user",
        entity_id=user_id,
        new_values={"reason": ban_request.reason},
        request=request,
    )

    await db.commit()
    return {"message": "User banned", "id": user_id}


@router.patch("/{user_id}/unban")
async def unban_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Unban a user."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_banned:
        raise HTTPException(status_code=400, detail="User is not banned")

    old_ban_reason = user.banned_reason

    user.is_banned = False
    user.banned_reason = None
    user.banned_at = None
    user.banned_by_id = None

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="unban_user",
        entity_type="user",
        entity_id=user_id,
        old_values={"banned_reason": old_ban_reason},
        request=request,
    )

    await db.commit()
    return {"message": "User unbanned", "id": user_id}


@router.patch("/{user_id}/activate")
async def activate_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Activate a deactivated user."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active:
        raise HTTPException(status_code=400, detail="User is already active")

    user.is_active = True

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="activate_user",
        entity_type="user",
        entity_id=user_id,
        new_values={"is_active": True},
        request=request,
    )

    await db.commit()
    return {"message": "User activated", "id": user_id}


@router.patch("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Deactivate a user."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Cannot deactivate users with higher or equal role
    if has_role_level(user.role, admin.role):
        raise HTTPException(status_code=403, detail="Cannot deactivate a user with equal or higher role")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is already deactivated")

    user.is_active = False

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="deactivate_user",
        entity_type="user",
        entity_id=user_id,
        new_values={"is_active": False},
        request=request,
    )

    await db.commit()
    return {"message": "User deactivated", "id": user_id}


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_super_admin),
):
    """Delete a user. Requires super admin."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Cannot delete super admins
    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Cannot delete super admin users")

    user_email = user.email

    # Delete user profile first (should cascade, but be explicit)
    if user.profile:
        await db.delete(user.profile)

    await db.delete(user)

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="delete_user",
        entity_type="user",
        entity_id=user_id,
        old_values={"email": user_email},
        request=request,
    )

    await db.commit()
    return {"message": "User deleted", "id": user_id}


@router.get("/{user_id}/activity")
async def get_user_activity(
    user_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get activity log for a specific user."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get audit log entries related to this user
    query = (
        select(AuditLog)
        .where(or_(
            AuditLog.admin_id == user_id,  # Actions performed by user
            and_(AuditLog.entity_type == "user", AuditLog.entity_id == user_id),  # Actions on user
        ))
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)

    activities = []
    for log in result.scalars():
        activities.append({
            "id": log.id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "performed_by": log.admin_id,
            "created_at": log.created_at,
        })

    return {"user_id": user_id, "activities": activities}


@router.get("/stats/by-role")
async def get_user_stats_by_role(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get user statistics by role."""
    stats = {}
    for role in UserRole:
        count = await db.scalar(
            select(func.count(User.id)).where(User.role == role)
        )
        stats[role.value] = count or 0

    total = sum(stats.values())
    active = await db.scalar(select(func.count(User.id)).where(User.is_active == True))
    banned = await db.scalar(select(func.count(User.id)).where(User.is_banned == True))

    return {
        "by_role": stats,
        "total": total,
        "active": active or 0,
        "banned": banned or 0,
    }
