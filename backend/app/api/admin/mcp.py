"""Admin MCP Server management API endpoints."""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.models.user import User
from app.models.mcp_server import MCPServer, MCPCategory
from app.models.admin import AuditLog
from app.core.deps import get_current_moderator, get_current_admin

router = APIRouter()


# Pydantic schemas
class MCPServerUpdate(BaseModel):
    """Schema for updating an MCP server."""
    category: Optional[MCPCategory] = None
    tags: Optional[List[str]] = None
    is_official: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    short_description: Optional[str] = None


class MCPServerAdminResponse(BaseModel):
    """Admin response for MCP server."""
    id: int
    name: str
    slug: str
    description: Optional[str]
    short_description: Optional[str]
    category: MCPCategory
    tags: Optional[List[str]]
    repository_url: Optional[str]
    stars: int
    downloads: int
    is_official: bool
    is_verified: bool
    is_featured: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class MCPStatsResponse(BaseModel):
    """MCP statistics response."""
    total: int
    by_category: dict
    official_count: int
    verified_count: int
    featured_count: int
    active_count: int


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
    """Log an admin action to the audit log."""
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


@router.get("", response_model=dict)
async def list_mcp_servers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: Optional[MCPCategory] = None,
    is_official: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = Query(default="created_at", pattern="^(created_at|name|stars|downloads)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """List all MCP servers with admin filters."""
    query = select(MCPServer)

    # Apply filters
    if category:
        query = query.where(MCPServer.category == category)
    if is_official is not None:
        query = query.where(MCPServer.is_official == is_official)
    if is_verified is not None:
        query = query.where(MCPServer.is_verified == is_verified)
    if is_featured is not None:
        query = query.where(MCPServer.is_featured == is_featured)
    if is_active is not None:
        query = query.where(MCPServer.is_active == is_active)
    if search:
        query = query.where(
            MCPServer.name.ilike(f"%{search}%") |
            MCPServer.description.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(MCPServer, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    servers = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [MCPServerAdminResponse.model_validate(s) for s in servers],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


@router.get("/stats", response_model=MCPStatsResponse)
async def get_mcp_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Get MCP server statistics."""
    # Total count
    total = await db.scalar(select(func.count(MCPServer.id)))

    # By category
    category_counts = {}
    for cat in MCPCategory:
        count = await db.scalar(
            select(func.count(MCPServer.id)).where(MCPServer.category == cat)
        )
        category_counts[cat.value] = count or 0

    # Status counts
    official_count = await db.scalar(
        select(func.count(MCPServer.id)).where(MCPServer.is_official == True)
    )
    verified_count = await db.scalar(
        select(func.count(MCPServer.id)).where(MCPServer.is_verified == True)
    )
    featured_count = await db.scalar(
        select(func.count(MCPServer.id)).where(MCPServer.is_featured == True)
    )
    active_count = await db.scalar(
        select(func.count(MCPServer.id)).where(MCPServer.is_active == True)
    )

    return MCPStatsResponse(
        total=total or 0,
        by_category=category_counts,
        official_count=official_count or 0,
        verified_count=verified_count or 0,
        featured_count=featured_count or 0,
        active_count=active_count or 0,
    )


@router.get("/{server_id}", response_model=MCPServerAdminResponse)
async def get_mcp_server(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Get a specific MCP server."""
    server = await db.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    return MCPServerAdminResponse.model_validate(server)


@router.patch("/{server_id}", response_model=MCPServerAdminResponse)
async def update_mcp_server(
    server_id: int,
    update_data: MCPServerUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Update an MCP server."""
    server = await db.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")

    old_values = {
        "category": server.category.value,
        "tags": server.tags,
        "is_official": server.is_official,
        "is_verified": server.is_verified,
        "is_featured": server.is_featured,
        "is_active": server.is_active,
    }

    # Apply updates
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(server, field, value)

    new_values = {
        "category": server.category.value,
        "tags": server.tags,
        "is_official": server.is_official,
        "is_verified": server.is_verified,
        "is_featured": server.is_featured,
        "is_active": server.is_active,
    }

    # Log audit
    await log_audit(
        db=db,
        admin_id=admin.id,
        action="update_mcp_server",
        entity_type="mcp_server",
        entity_id=server_id,
        old_values=old_values,
        new_values=new_values,
        request=request,
    )

    await db.commit()
    await db.refresh(server)

    return MCPServerAdminResponse.model_validate(server)


@router.post("/{server_id}/verify", response_model=dict)
async def verify_mcp_server(
    server_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Mark an MCP server as verified."""
    server = await db.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")

    old_verified = server.is_verified
    server.is_verified = True

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="verify_mcp_server",
        entity_type="mcp_server",
        entity_id=server_id,
        old_values={"is_verified": old_verified},
        new_values={"is_verified": True, "name": server.name},
        request=request,
    )

    await db.commit()
    return {"message": "MCP server verified", "id": server_id}


@router.post("/{server_id}/unverify", response_model=dict)
async def unverify_mcp_server(
    server_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Remove verification from an MCP server."""
    server = await db.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")

    old_verified = server.is_verified
    server.is_verified = False

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="unverify_mcp_server",
        entity_type="mcp_server",
        entity_id=server_id,
        old_values={"is_verified": old_verified},
        new_values={"is_verified": False, "name": server.name},
        request=request,
    )

    await db.commit()
    return {"message": "MCP server unverified", "id": server_id}


@router.post("/{server_id}/feature", response_model=dict)
async def feature_mcp_server(
    server_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Mark an MCP server as featured."""
    server = await db.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")

    old_featured = server.is_featured
    server.is_featured = True

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="feature_mcp_server",
        entity_type="mcp_server",
        entity_id=server_id,
        old_values={"is_featured": old_featured},
        new_values={"is_featured": True, "name": server.name},
        request=request,
    )

    await db.commit()
    return {"message": "MCP server featured", "id": server_id}


@router.post("/{server_id}/unfeature", response_model=dict)
async def unfeature_mcp_server(
    server_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Remove featured status from an MCP server."""
    server = await db.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")

    old_featured = server.is_featured
    server.is_featured = False

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="unfeature_mcp_server",
        entity_type="mcp_server",
        entity_id=server_id,
        old_values={"is_featured": old_featured},
        new_values={"is_featured": False, "name": server.name},
        request=request,
    )

    await db.commit()
    return {"message": "MCP server unfeatured", "id": server_id}


@router.post("/{server_id}/deactivate", response_model=dict)
async def deactivate_mcp_server(
    server_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Deactivate (soft delete) an MCP server."""
    server = await db.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")

    server.is_active = False

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="deactivate_mcp_server",
        entity_type="mcp_server",
        entity_id=server_id,
        old_values={"is_active": True},
        new_values={"is_active": False, "name": server.name},
        request=request,
    )

    await db.commit()
    return {"message": "MCP server deactivated", "id": server_id}


@router.post("/{server_id}/activate", response_model=dict)
async def activate_mcp_server(
    server_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Reactivate an MCP server."""
    server = await db.get(MCPServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")

    server.is_active = True

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="activate_mcp_server",
        entity_type="mcp_server",
        entity_id=server_id,
        old_values={"is_active": False},
        new_values={"is_active": True, "name": server.name},
        request=request,
    )

    await db.commit()
    return {"message": "MCP server activated", "id": server_id}


class BulkMCPAction(BaseModel):
    """Schema for bulk MCP server actions."""
    server_ids: List[int]
    action: str  # verify, unverify, feature, unfeature, activate, deactivate


@router.post("/bulk-action", response_model=dict)
async def bulk_mcp_action(
    bulk_request: BulkMCPAction,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Perform bulk action on multiple MCP servers."""
    valid_actions = ["verify", "unverify", "feature", "unfeature", "activate", "deactivate"]
    if bulk_request.action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of: {valid_actions}")

    action_field_map = {
        "verify": ("is_verified", True),
        "unverify": ("is_verified", False),
        "feature": ("is_featured", True),
        "unfeature": ("is_featured", False),
        "activate": ("is_active", True),
        "deactivate": ("is_active", False),
    }

    field, value = action_field_map[bulk_request.action]
    processed = []
    errors = []

    for server_id in bulk_request.server_ids:
        server = await db.get(MCPServer, server_id)
        if not server:
            errors.append({"id": server_id, "error": "Not found"})
            continue

        old_value = getattr(server, field)
        setattr(server, field, value)
        processed.append(server_id)

    if processed:
        await log_audit(
            db=db,
            admin_id=admin.id,
            action=f"bulk_{bulk_request.action}_mcp_servers",
            entity_type="mcp_server",
            entity_id=None,
            new_values={"ids": processed, "action": bulk_request.action},
            request=request,
        )

    await db.commit()

    return {
        "message": f"Bulk {bulk_request.action} completed",
        "processed": len(processed),
        "errors": errors,
    }
