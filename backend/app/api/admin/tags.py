"""Admin tags management API endpoints."""
import re
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from app.db.database import get_db
from app.models.user import User
from app.models.admin import Tag, ContentTag, AuditLog
from app.core.deps import get_current_moderator, get_current_admin
from app.schemas.admin import (
    TagCreate,
    TagUpdate,
    TagResponse,
    TagListResponse,
)

router = APIRouter()


def create_slug(name: str) -> str:
    """Create URL-friendly slug from name."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:50]


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


@router.get("", response_model=TagListResponse)
async def list_tags(
    search: Optional[str] = None,
    featured_only: bool = False,
    sort_by: str = Query("usage_count", pattern=r"^(name|usage_count|created_at)$"),
    sort_order: str = Query("desc", pattern=r"^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """List all tags with filtering and sorting."""
    # Build query
    query = select(Tag)
    count_query = select(func.count(Tag.id))

    # Apply filters
    if search:
        query = query.where(Tag.name.ilike(f"%{search}%"))
        count_query = count_query.where(Tag.name.ilike(f"%{search}%"))

    if featured_only:
        query = query.where(Tag.is_featured == True)
        count_query = count_query.where(Tag.is_featured == True)

    # Get total count
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(Tag, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    tags = [TagResponse.model_validate(tag) for tag in result.scalars()]

    return TagListResponse(
        items=tags,
        total=total or 0,
        page=page,
        page_size=page_size,
    )


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Get a specific tag."""
    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagResponse.model_validate(tag)


@router.post("", response_model=TagResponse)
async def create_tag(
    tag_data: TagCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Create a new tag."""
    # Check if name already exists
    existing = await db.scalar(
        select(Tag).where(Tag.name == tag_data.name)
    )
    if existing:
        raise HTTPException(status_code=400, detail="Tag with this name already exists")

    # Create slug
    slug = create_slug(tag_data.name)

    # Check if slug exists and make unique if needed
    slug_exists = await db.scalar(select(Tag).where(Tag.slug == slug))
    if slug_exists:
        count = await db.scalar(select(func.count(Tag.id)).where(Tag.slug.like(f"{slug}%")))
        slug = f"{slug}-{count + 1}"

    tag = Tag(
        name=tag_data.name,
        slug=slug,
        description=tag_data.description,
        color=tag_data.color,
        is_featured=tag_data.is_featured,
        usage_count=0,
    )
    db.add(tag)
    await db.flush()

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="create_tag",
        entity_type="tag",
        entity_id=tag.id,
        new_values={"name": tag.name, "slug": tag.slug},
        request=request,
    )

    await db.commit()
    await db.refresh(tag)
    return TagResponse.model_validate(tag)


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Update a tag."""
    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    old_values = {"name": tag.name, "description": tag.description, "color": tag.color}

    # Check if new name conflicts
    if tag_data.name and tag_data.name != tag.name:
        existing = await db.scalar(
            select(Tag).where(Tag.name == tag_data.name)
        )
        if existing:
            raise HTTPException(status_code=400, detail="Tag with this name already exists")
        tag.name = tag_data.name
        tag.slug = create_slug(tag_data.name)

    if tag_data.description is not None:
        tag.description = tag_data.description
    if tag_data.color is not None:
        tag.color = tag_data.color
    if tag_data.is_featured is not None:
        tag.is_featured = tag_data.is_featured

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="update_tag",
        entity_type="tag",
        entity_id=tag_id,
        old_values=old_values,
        new_values={"name": tag.name, "description": tag.description, "color": tag.color},
        request=request,
    )

    await db.commit()
    await db.refresh(tag)
    return TagResponse.model_validate(tag)


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Delete a tag."""
    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag_name = tag.name

    # Delete all content_tags associations (cascade should handle this, but be explicit)
    await db.execute(delete(ContentTag).where(ContentTag.tag_id == tag_id))

    # Delete the tag
    await db.delete(tag)

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="delete_tag",
        entity_type="tag",
        entity_id=tag_id,
        old_values={"name": tag_name},
        request=request,
    )

    await db.commit()
    return {"message": "Tag deleted", "id": tag_id}


@router.post("/merge")
async def merge_tags(
    source_tag_ids: List[int],
    target_tag_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Merge multiple tags into a single target tag."""
    # Validate target tag exists
    target_tag = await db.get(Tag, target_tag_id)
    if not target_tag:
        raise HTTPException(status_code=404, detail="Target tag not found")

    if target_tag_id in source_tag_ids:
        raise HTTPException(status_code=400, detail="Target tag cannot be in source tags")

    merged_count = 0
    deleted_tags = []

    for source_id in source_tag_ids:
        source_tag = await db.get(Tag, source_id)
        if not source_tag:
            continue

        deleted_tags.append(source_tag.name)

        # Move all content tags from source to target
        content_tags_query = select(ContentTag).where(ContentTag.tag_id == source_id)
        result = await db.execute(content_tags_query)

        for ct in result.scalars():
            # Check if target already has this content tagged
            existing = await db.scalar(
                select(ContentTag.id).where(
                    ContentTag.tag_id == target_tag_id,
                    ContentTag.content_type == ct.content_type,
                    ContentTag.content_id == ct.content_id,
                )
            )
            if not existing:
                ct.tag_id = target_tag_id
                merged_count += 1
            else:
                await db.delete(ct)

        # Update target usage count
        target_tag.usage_count += source_tag.usage_count

        # Delete source tag
        await db.delete(source_tag)

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="merge_tags",
        entity_type="tag",
        entity_id=target_tag_id,
        new_values={
            "merged_from": deleted_tags,
            "target": target_tag.name,
            "content_moved": merged_count,
        },
        request=request,
    )

    await db.commit()
    return {
        "message": "Tags merged successfully",
        "target_tag": target_tag.name,
        "merged_tags": deleted_tags,
        "content_items_affected": merged_count,
    }


@router.delete("/cleanup/unused")
async def delete_unused_tags(
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Delete all tags with zero usage count."""
    # Get unused tags
    query = select(Tag).where(Tag.usage_count == 0)
    result = await db.execute(query)
    unused_tags = list(result.scalars())

    deleted_names = [tag.name for tag in unused_tags]

    for tag in unused_tags:
        await db.delete(tag)

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="cleanup_unused_tags",
        entity_type="tag",
        entity_id=None,
        new_values={"deleted": deleted_names},
        request=request,
    )

    await db.commit()
    return {
        "message": "Unused tags deleted",
        "deleted_count": len(deleted_names),
        "deleted_tags": deleted_names,
    }


@router.get("/suggestions/{content_type}/{content_id}")
async def get_tag_suggestions(
    content_type: str,
    content_id: int,
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Get tag suggestions for a content item based on similar content."""
    # Get existing tags for this content
    existing_query = select(ContentTag.tag_id).where(
        ContentTag.content_type == content_type,
        ContentTag.content_id == content_id,
    )
    existing_result = await db.execute(existing_query)
    existing_tag_ids = [row[0] for row in existing_result]

    # Get most used tags for this content type, excluding already assigned
    query = (
        select(Tag)
        .join(ContentTag, ContentTag.tag_id == Tag.id)
        .where(ContentTag.content_type == content_type)
    )
    if existing_tag_ids:
        query = query.where(Tag.id.not_in(existing_tag_ids))

    query = (
        query
        .group_by(Tag.id)
        .order_by(func.count(ContentTag.id).desc())
        .limit(limit)
    )

    result = await db.execute(query)
    suggestions = [TagResponse.model_validate(tag) for tag in result.scalars()]

    return {"suggestions": suggestions}
