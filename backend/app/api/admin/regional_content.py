"""Admin regional content management endpoints."""
import re
import csv
import io
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.user import User
from app.models.region import Region
from app.models.regional_content import RegionalContent, RegionalContentType
from app.models.admin import AuditLog, ContentStatus
from app.core.deps import get_current_admin
from app.schemas.region import (
    RegionalContentCreate,
    RegionalContentUpdate,
    RegionalContentResponse,
    RegionalContentListResponse,
    RegionalContentBulkCreate,
    RegionalContentBulkDelete,
    RegionalContentStatusUpdate,
)

router = APIRouter()


def create_slug(title: str) -> str:
    """Create URL-friendly slug from title."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:550]


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


@router.get("", response_model=RegionalContentListResponse)
async def list_regional_content(
    region_id: Optional[int] = None,
    content_type: Optional[RegionalContentType] = None,
    moderation_status: Optional[ContentStatus] = None,
    is_active: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """List regional content with filters and pagination."""
    query = select(RegionalContent).options(selectinload(RegionalContent.region))

    if region_id is not None:
        query = query.where(RegionalContent.region_id == region_id)
    if content_type is not None:
        query = query.where(RegionalContent.content_type == content_type)
    if moderation_status is not None:
        query = query.where(RegionalContent.moderation_status == moderation_status)
    if is_active is not None:
        query = query.where(RegionalContent.is_active == is_active)
    if is_featured is not None:
        query = query.where(RegionalContent.is_featured == is_featured)
    if search:
        query = query.where(RegionalContent.title.ilike(f"%{search}%"))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply pagination
    query = query.order_by(RegionalContent.sort_order, RegionalContent.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return RegionalContentListResponse(
        items=[RegionalContentResponse.model_validate(item) for item in items],
        total=total or 0,
        page=page,
        page_size=page_size
    )


@router.get("/{content_id}", response_model=RegionalContentResponse)
async def get_regional_content(
    content_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get a specific regional content item."""
    query = select(RegionalContent).where(RegionalContent.id == content_id).options(
        selectinload(RegionalContent.region)
    )
    result = await db.execute(query)
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(status_code=404, detail="Regional content not found")

    return RegionalContentResponse.model_validate(content)


@router.post("", response_model=RegionalContentResponse)
async def create_regional_content(
    content_data: RegionalContentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Create a new regional content item."""
    # Validate region exists
    region = await db.get(Region, content_data.region_id)
    if not region:
        raise HTTPException(status_code=400, detail="Region not found")

    # Create slug
    slug = create_slug(content_data.title)
    slug_exists = await db.scalar(select(RegionalContent).where(RegionalContent.slug == slug))
    if slug_exists:
        count = await db.scalar(
            select(func.count(RegionalContent.id)).where(RegionalContent.slug.like(f"{slug}%"))
        )
        slug = f"{slug}-{count + 1}"

    content = RegionalContent(
        region_id=content_data.region_id,
        content_type=content_data.content_type,
        title=content_data.title,
        slug=slug,
        description=content_data.description,
        url=content_data.url,
        image_url=content_data.image_url,
        data=content_data.data,
        is_active=content_data.is_active,
        is_featured=content_data.is_featured,
        sort_order=content_data.sort_order,
        moderation_status=ContentStatus.PENDING,
        created_by_id=admin.id,
    )
    db.add(content)
    await db.flush()

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="create_regional_content",
        entity_type="regional_content",
        entity_id=content.id,
        new_values={"title": content.title, "region_id": content.region_id},
        request=request,
    )

    await db.commit()

    # Reload with region
    query = select(RegionalContent).where(RegionalContent.id == content.id).options(
        selectinload(RegionalContent.region)
    )
    result = await db.execute(query)
    content = result.scalar_one()

    return RegionalContentResponse.model_validate(content)


@router.put("/{content_id}", response_model=RegionalContentResponse)
async def update_regional_content(
    content_id: int,
    content_data: RegionalContentUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Update a regional content item."""
    query = select(RegionalContent).where(RegionalContent.id == content_id).options(
        selectinload(RegionalContent.region)
    )
    result = await db.execute(query)
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(status_code=404, detail="Regional content not found")

    old_values = {"title": content.title, "region_id": content.region_id}

    if content_data.region_id is not None:
        region = await db.get(Region, content_data.region_id)
        if not region:
            raise HTTPException(status_code=400, detail="Region not found")
        content.region_id = content_data.region_id

    if content_data.content_type is not None:
        content.content_type = content_data.content_type

    if content_data.title is not None:
        content.title = content_data.title
        content.slug = create_slug(content_data.title)

    if content_data.description is not None:
        content.description = content_data.description
    if content_data.url is not None:
        content.url = content_data.url
    if content_data.image_url is not None:
        content.image_url = content_data.image_url
    if content_data.data is not None:
        content.data = content_data.data
    if content_data.is_active is not None:
        content.is_active = content_data.is_active
    if content_data.is_featured is not None:
        content.is_featured = content_data.is_featured
    if content_data.sort_order is not None:
        content.sort_order = content_data.sort_order

    content.updated_by_id = admin.id

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="update_regional_content",
        entity_type="regional_content",
        entity_id=content_id,
        old_values=old_values,
        new_values={"title": content.title, "region_id": content.region_id},
        request=request,
    )

    await db.commit()
    await db.refresh(content)

    return RegionalContentResponse.model_validate(content)


@router.delete("/{content_id}")
async def delete_regional_content(
    content_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Delete a regional content item."""
    content = await db.get(RegionalContent, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Regional content not found")

    content_title = content.title
    await db.delete(content)

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="delete_regional_content",
        entity_type="regional_content",
        entity_id=content_id,
        old_values={"title": content_title},
        request=request,
    )

    await db.commit()
    return {"message": "Regional content deleted", "id": content_id}


@router.post("/bulk", response_model=dict)
async def bulk_create_regional_content(
    bulk_data: RegionalContentBulkCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Bulk create regional content items."""
    created_ids = []

    for item_data in bulk_data.items:
        # Validate region exists
        region = await db.get(Region, item_data.region_id)
        if not region:
            continue

        # Create slug
        slug = create_slug(item_data.title)
        slug_exists = await db.scalar(select(RegionalContent).where(RegionalContent.slug == slug))
        if slug_exists:
            count = await db.scalar(
                select(func.count(RegionalContent.id)).where(RegionalContent.slug.like(f"{slug}%"))
            )
            slug = f"{slug}-{count + 1}"

        content = RegionalContent(
            region_id=item_data.region_id,
            content_type=item_data.content_type,
            title=item_data.title,
            slug=slug,
            description=item_data.description,
            url=item_data.url,
            image_url=item_data.image_url,
            data=item_data.data,
            is_active=item_data.is_active,
            is_featured=item_data.is_featured,
            sort_order=item_data.sort_order,
            moderation_status=ContentStatus.PENDING,
            created_by_id=admin.id,
        )
        db.add(content)
        await db.flush()
        created_ids.append(content.id)

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="bulk_create_regional_content",
        entity_type="regional_content",
        entity_id=0,
        new_values={"count": len(created_ids), "ids": created_ids},
        request=request,
    )

    await db.commit()
    return {"message": f"Created {len(created_ids)} items", "ids": created_ids}


@router.delete("/bulk")
async def bulk_delete_regional_content(
    bulk_data: RegionalContentBulkDelete,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Bulk delete regional content items."""
    deleted_count = 0

    for content_id in bulk_data.ids:
        content = await db.get(RegionalContent, content_id)
        if content:
            await db.delete(content)
            deleted_count += 1

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="bulk_delete_regional_content",
        entity_type="regional_content",
        entity_id=0,
        old_values={"ids": bulk_data.ids},
        new_values={"deleted_count": deleted_count},
        request=request,
    )

    await db.commit()
    return {"message": f"Deleted {deleted_count} items", "deleted_count": deleted_count}


@router.patch("/{content_id}/status")
async def update_regional_content_status(
    content_id: int,
    status_data: RegionalContentStatusUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Update the moderation status of a regional content item."""
    content = await db.get(RegionalContent, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Regional content not found")

    old_status = content.moderation_status
    content.moderation_status = status_data.status
    content.updated_by_id = admin.id

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="update_regional_content_status",
        entity_type="regional_content",
        entity_id=content_id,
        old_values={"status": old_status.value},
        new_values={"status": status_data.status.value, "reason": status_data.reason},
        request=request,
    )

    await db.commit()
    return {
        "message": f"Status updated to {status_data.status.value}",
        "id": content_id,
        "status": status_data.status.value
    }


@router.post("/{content_id}/duplicate")
async def duplicate_regional_content(
    content_id: int,
    target_region_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Duplicate a regional content item to another region."""
    content = await db.get(RegionalContent, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Regional content not found")

    target_region = await db.get(Region, target_region_id)
    if not target_region:
        raise HTTPException(status_code=400, detail="Target region not found")

    # Create slug
    slug = create_slug(content.title)
    slug_exists = await db.scalar(select(RegionalContent).where(RegionalContent.slug == slug))
    if slug_exists:
        count = await db.scalar(
            select(func.count(RegionalContent.id)).where(RegionalContent.slug.like(f"{slug}%"))
        )
        slug = f"{slug}-{count + 1}"

    new_content = RegionalContent(
        region_id=target_region_id,
        content_type=content.content_type,
        title=content.title,
        slug=slug,
        description=content.description,
        url=content.url,
        image_url=content.image_url,
        data=content.data,
        is_active=content.is_active,
        is_featured=False,  # Don't copy featured status
        sort_order=content.sort_order,
        moderation_status=ContentStatus.PENDING,
        created_by_id=admin.id,
    )
    db.add(new_content)
    await db.flush()

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="duplicate_regional_content",
        entity_type="regional_content",
        entity_id=new_content.id,
        new_values={
            "source_id": content_id,
            "target_region_id": target_region_id,
            "title": new_content.title
        },
        request=request,
    )

    await db.commit()
    return {"message": "Content duplicated", "new_id": new_content.id}


@router.get("/export/csv")
async def export_regional_content_csv(
    region_id: Optional[int] = None,
    content_type: Optional[RegionalContentType] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Export regional content to CSV."""
    query = select(RegionalContent).options(selectinload(RegionalContent.region))

    if region_id is not None:
        query = query.where(RegionalContent.region_id == region_id)
    if content_type is not None:
        query = query.where(RegionalContent.content_type == content_type)

    query = query.order_by(RegionalContent.region_id, RegionalContent.content_type, RegionalContent.sort_order)
    result = await db.execute(query)
    items = result.scalars().all()

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        "ID", "Region Code", "Region Name", "Content Type", "Title",
        "Description", "URL", "Image URL", "Is Active", "Is Featured",
        "Moderation Status", "Sort Order", "Created At"
    ])

    # Data rows
    for item in items:
        writer.writerow([
            item.id,
            item.region.code if item.region else "",
            item.region.name if item.region else "",
            item.content_type.value,
            item.title,
            item.description or "",
            item.url or "",
            item.image_url or "",
            item.is_active,
            item.is_featured,
            item.moderation_status.value,
            item.sort_order,
            item.created_at.isoformat() if item.created_at else ""
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=regional_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )
