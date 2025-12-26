"""Admin region management endpoints."""
import re
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.user import User
from app.models.region import Region, RegionType
from app.models.admin import AuditLog
from app.core.deps import get_current_admin
from app.schemas.region import (
    RegionCreate,
    RegionUpdate,
    RegionResponse,
    RegionWithChildrenResponse,
    RegionTreeResponse,
    RegionListResponse,
)

router = APIRouter()


def create_slug(name: str) -> str:
    """Create URL-friendly slug from name."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:100]


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


def build_region_tree(regions: List[Region], parent_id: Optional[int] = None) -> List[dict]:
    """Build a hierarchical tree from flat region list."""
    tree = []
    for region in regions:
        if region.parent_id == parent_id:
            children = build_region_tree(regions, region.id)
            region_dict = {
                "id": region.id,
                "code": region.code,
                "name": region.name,
                "slug": region.slug,
                "region_type": region.region_type,
                "parent_id": region.parent_id,
                "iso_code": region.iso_code,
                "timezone": region.timezone,
                "description": region.description,
                "is_active": region.is_active,
                "sort_order": region.sort_order,
                "created_at": region.created_at,
                "updated_at": region.updated_at,
                "children": children,
            }
            tree.append(region_dict)
    return tree


@router.get("", response_model=RegionListResponse)
async def list_regions(
    region_type: Optional[RegionType] = None,
    parent_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """List all regions with optional filters."""
    query = select(Region)

    if region_type:
        query = query.where(Region.region_type == region_type)
    if parent_id is not None:
        query = query.where(Region.parent_id == parent_id)
    if is_active is not None:
        query = query.where(Region.is_active == is_active)

    query = query.order_by(Region.sort_order, Region.name)
    result = await db.execute(query)
    regions = result.scalars().all()

    return RegionListResponse(
        items=[RegionResponse.model_validate(r) for r in regions],
        total=len(regions)
    )


@router.get("/tree", response_model=RegionTreeResponse)
async def get_region_tree(
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get the full region hierarchy as a tree."""
    query = select(Region).order_by(Region.sort_order, Region.name)
    if is_active is not None:
        query = query.where(Region.is_active == is_active)

    result = await db.execute(query)
    regions = result.scalars().all()

    tree = build_region_tree(list(regions), None)
    return RegionTreeResponse(regions=tree)


@router.get("/{region_id}", response_model=RegionWithChildrenResponse)
async def get_region(
    region_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get a specific region with its children."""
    query = select(Region).where(Region.id == region_id).options(
        selectinload(Region.children)
    )
    result = await db.execute(query)
    region = result.scalar_one_or_none()

    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    return RegionWithChildrenResponse.model_validate(region)


@router.post("", response_model=RegionResponse)
async def create_region(
    region_data: RegionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Create a new region."""
    # Check if code already exists
    existing = await db.scalar(select(Region).where(Region.code == region_data.code))
    if existing:
        raise HTTPException(status_code=400, detail="Region code already exists")

    # Create slug
    slug = create_slug(region_data.name)
    slug_exists = await db.scalar(select(Region).where(Region.slug == slug))
    if slug_exists:
        count = await db.scalar(select(func.count(Region.id)).where(Region.slug.like(f"{slug}%")))
        slug = f"{slug}-{count + 1}"

    # Validate parent exists if specified
    if region_data.parent_id:
        parent = await db.get(Region, region_data.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="Parent region not found")

    region = Region(
        code=region_data.code,
        name=region_data.name,
        slug=slug,
        region_type=region_data.region_type,
        parent_id=region_data.parent_id,
        iso_code=region_data.iso_code,
        timezone=region_data.timezone,
        description=region_data.description,
        is_active=region_data.is_active,
        sort_order=region_data.sort_order,
    )
    db.add(region)
    await db.flush()

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="create_region",
        entity_type="region",
        entity_id=region.id,
        new_values={"code": region.code, "name": region.name},
        request=request,
    )

    await db.commit()
    await db.refresh(region)
    return RegionResponse.model_validate(region)


@router.put("/{region_id}", response_model=RegionResponse)
async def update_region(
    region_id: int,
    region_data: RegionUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Update a region."""
    region = await db.get(Region, region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    old_values = {"code": region.code, "name": region.name, "is_active": region.is_active}

    if region_data.code is not None:
        # Check if new code already exists
        existing = await db.scalar(
            select(Region).where(Region.code == region_data.code, Region.id != region_id)
        )
        if existing:
            raise HTTPException(status_code=400, detail="Region code already exists")
        region.code = region_data.code

    if region_data.name is not None:
        region.name = region_data.name
        region.slug = create_slug(region_data.name)

    if region_data.region_type is not None:
        region.region_type = region_data.region_type

    if region_data.parent_id is not None:
        if region_data.parent_id == region_id:
            raise HTTPException(status_code=400, detail="Region cannot be its own parent")
        if region_data.parent_id != 0:
            parent = await db.get(Region, region_data.parent_id)
            if not parent:
                raise HTTPException(status_code=400, detail="Parent region not found")
        region.parent_id = region_data.parent_id if region_data.parent_id != 0 else None

    if region_data.iso_code is not None:
        region.iso_code = region_data.iso_code
    if region_data.timezone is not None:
        region.timezone = region_data.timezone
    if region_data.description is not None:
        region.description = region_data.description
    if region_data.is_active is not None:
        region.is_active = region_data.is_active
    if region_data.sort_order is not None:
        region.sort_order = region_data.sort_order

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="update_region",
        entity_type="region",
        entity_id=region_id,
        old_values=old_values,
        new_values={"code": region.code, "name": region.name, "is_active": region.is_active},
        request=request,
    )

    await db.commit()
    await db.refresh(region)
    return RegionResponse.model_validate(region)


@router.delete("/{region_id}")
async def delete_region(
    region_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Delete a region."""
    region = await db.get(Region, region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    # Check if region has children
    children_count = await db.scalar(
        select(func.count(Region.id)).where(Region.parent_id == region_id)
    )
    if children_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete region with {children_count} child regions. Delete children first."
        )

    region_name = region.name
    await db.delete(region)

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="delete_region",
        entity_type="region",
        entity_id=region_id,
        old_values={"name": region_name},
        request=request,
    )

    await db.commit()
    return {"message": "Region deleted", "id": region_id}


@router.patch("/{region_id}/toggle")
async def toggle_region(
    region_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Toggle a region's active status."""
    region = await db.get(Region, region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    old_state = region.is_active
    region.is_active = not region.is_active

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="toggle_region",
        entity_type="region",
        entity_id=region_id,
        old_values={"is_active": old_state},
        new_values={"is_active": region.is_active},
        request=request,
    )

    await db.commit()
    return {
        "message": f"Region {'activated' if region.is_active else 'deactivated'}",
        "id": region_id,
        "is_active": region.is_active
    }
