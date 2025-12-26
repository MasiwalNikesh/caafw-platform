"""Admin audit log API endpoints."""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.db.database import get_db
from app.models.user import User
from app.models.admin import AuditLog
from app.core.deps import get_current_admin
from app.schemas.admin import (
    AuditLogResponse,
    AuditLogListResponse,
)

router = APIRouter()


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    admin_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """List audit log entries with filtering."""
    # Build query
    query = (
        select(AuditLog, User.name, User.email)
        .join(User, AuditLog.admin_id == User.id)
    )
    count_query = select(func.count(AuditLog.id))

    # Apply filters
    filters = []
    if admin_id:
        filters.append(AuditLog.admin_id == admin_id)
    if action:
        filters.append(AuditLog.action.ilike(f"%{action}%"))
    if entity_type:
        filters.append(AuditLog.entity_type == entity_type)
    if entity_id:
        filters.append(AuditLog.entity_id == entity_id)
    if start_date:
        filters.append(AuditLog.created_at >= start_date)
    if end_date:
        filters.append(AuditLog.created_at <= end_date)

    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    # Get total count
    total = await db.scalar(count_query)

    # Apply ordering and pagination
    query = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)

    logs = []
    for audit_log, admin_name, admin_email in result:
        logs.append(AuditLogResponse(
            id=audit_log.id,
            admin_id=audit_log.admin_id,
            admin_name=admin_name,
            admin_email=admin_email,
            action=audit_log.action,
            entity_type=audit_log.entity_type,
            entity_id=audit_log.entity_id,
            old_values=audit_log.old_values,
            new_values=audit_log.new_values,
            ip_address=audit_log.ip_address,
            created_at=audit_log.created_at,
        ))

    return AuditLogListResponse(
        items=logs,
        total=total or 0,
        page=page,
        page_size=page_size,
    )


@router.get("/actions")
async def list_action_types(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get list of unique action types in the audit log."""
    query = select(AuditLog.action).distinct().order_by(AuditLog.action)
    result = await db.execute(query)
    actions = [row[0] for row in result]
    return {"actions": actions}


@router.get("/entity-types")
async def list_entity_types(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get list of unique entity types in the audit log."""
    query = select(AuditLog.entity_type).distinct().order_by(AuditLog.entity_type)
    result = await db.execute(query)
    entity_types = [row[0] for row in result]
    return {"entity_types": entity_types}


@router.get("/admins")
async def list_admins_with_activity(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get list of admins who have audit log entries."""
    query = (
        select(User.id, User.name, User.email, func.count(AuditLog.id).label("action_count"))
        .join(AuditLog, User.id == AuditLog.admin_id)
        .group_by(User.id, User.name, User.email)
        .order_by(func.count(AuditLog.id).desc())
    )
    result = await db.execute(query)

    admins = []
    for user_id, name, email, action_count in result:
        admins.append({
            "id": user_id,
            "name": name or email,
            "email": email,
            "action_count": action_count,
        })

    return {"admins": admins}


@router.get("/stats")
async def get_audit_stats(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get audit log statistics for the specified period."""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Total actions
    total = await db.scalar(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= start_date)
    )

    # Actions by type
    actions_query = (
        select(AuditLog.action, func.count(AuditLog.id))
        .where(AuditLog.created_at >= start_date)
        .group_by(AuditLog.action)
        .order_by(func.count(AuditLog.id).desc())
        .limit(10)
    )
    actions_result = await db.execute(actions_query)
    top_actions = {row[0]: row[1] for row in actions_result}

    # Actions by entity type
    entity_query = (
        select(AuditLog.entity_type, func.count(AuditLog.id))
        .where(AuditLog.created_at >= start_date)
        .group_by(AuditLog.entity_type)
    )
    entity_result = await db.execute(entity_query)
    by_entity = {row[0]: row[1] for row in entity_result}

    # Most active admins
    admins_query = (
        select(User.name, User.email, func.count(AuditLog.id))
        .join(AuditLog, User.id == AuditLog.admin_id)
        .where(AuditLog.created_at >= start_date)
        .group_by(User.id, User.name, User.email)
        .order_by(func.count(AuditLog.id).desc())
        .limit(5)
    )
    admins_result = await db.execute(admins_query)
    most_active = [
        {"name": name or email, "actions": count}
        for name, email, count in admins_result
    ]

    # Daily activity for charts
    daily_query = (
        select(
            func.date(AuditLog.created_at).label("date"),
            func.count(AuditLog.id)
        )
        .where(AuditLog.created_at >= start_date)
        .group_by(func.date(AuditLog.created_at))
        .order_by(func.date(AuditLog.created_at))
    )
    daily_result = await db.execute(daily_query)
    daily_activity = [
        {"date": str(row[0]), "count": row[1]}
        for row in daily_result
    ]

    return {
        "period_days": days,
        "total_actions": total or 0,
        "top_actions": top_actions,
        "by_entity_type": by_entity,
        "most_active_admins": most_active,
        "daily_activity": daily_activity,
    }


@router.get("/{log_id}")
async def get_audit_log_entry(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get a specific audit log entry with full details."""
    query = (
        select(AuditLog, User.name, User.email)
        .join(User, AuditLog.admin_id == User.id)
        .where(AuditLog.id == log_id)
    )
    result = await db.execute(query)
    row = result.first()

    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Audit log entry not found")

    audit_log, admin_name, admin_email = row

    return {
        "id": audit_log.id,
        "admin": {
            "id": audit_log.admin_id,
            "name": admin_name,
            "email": admin_email,
        },
        "action": audit_log.action,
        "entity_type": audit_log.entity_type,
        "entity_id": audit_log.entity_id,
        "old_values": audit_log.old_values,
        "new_values": audit_log.new_values,
        "ip_address": audit_log.ip_address,
        "user_agent": audit_log.user_agent,
        "created_at": audit_log.created_at,
    }
