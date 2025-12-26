"""Admin content moderation API endpoints."""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.db.database import get_db
from app.models.user import User
from app.models.admin import ContentStatus, AuditLog, ContentModeration, ContentTag, Tag
from app.models.news import NewsArticle
from app.models.job import Job
from app.models.product import Product
from app.models.event import Event
from app.models.research import ResearchPaper
from app.core.deps import get_current_moderator, get_current_admin
from app.schemas.admin import (
    ModerationAction,
    BulkModerationRequest,
    ContentModerationResponse,
    AdminContentItem,
    AdminContentListResponse,
)

router = APIRouter()

# Content type to model mapping
CONTENT_MODELS = {
    "news": NewsArticle,
    "job": Job,
    "product": Product,
    "event": Event,
    "research": ResearchPaper,
}


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


async def log_moderation(
    db: AsyncSession,
    content_type: str,
    content_id: int,
    action: str,
    previous_status: str,
    new_status: str,
    reviewed_by: int,
    reason: str = None,
    notes: str = None,
):
    """Log moderation history."""
    moderation = ContentModeration(
        content_type=content_type,
        content_id=content_id,
        action=action,
        previous_status=previous_status,
        new_status=new_status,
        reviewed_by=reviewed_by,
        reason=reason,
        notes=notes,
    )
    db.add(moderation)
    await db.flush()


def get_title_from_content(content, content_type: str) -> str:
    """Extract title from content item."""
    if content_type == "job":
        return f"{content.title} at {content.company_name}"
    elif content_type == "product":
        return content.name
    else:
        return content.title


@router.get("", response_model=AdminContentListResponse)
async def list_content(
    content_type: Optional[str] = Query(None, pattern=r"^(news|job|product|event|research)$"),
    status_filter: Optional[ContentStatus] = Query(None, alias="status"),
    source: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """List all content with filters."""
    items = []
    total = 0
    status_counts = {s.value: 0 for s in ContentStatus}

    content_types = [content_type] if content_type else list(CONTENT_MODELS.keys())

    for ct in content_types:
        model = CONTENT_MODELS[ct]

        # Build base query
        query = select(model)
        count_query = select(func.count(model.id))

        # Apply filters
        filters = []
        if status_filter:
            filters.append(model.moderation_status == status_filter)

        if search:
            if ct == "job":
                filters.append(or_(
                    model.title.ilike(f"%{search}%"),
                    model.company_name.ilike(f"%{search}%"),
                ))
            elif ct == "product":
                filters.append(model.name.ilike(f"%{search}%"))
            else:
                filters.append(model.title.ilike(f"%{search}%"))

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Get count for this content type
        type_count = await db.scalar(count_query)
        total += type_count or 0

        # Get status counts
        for s in ContentStatus:
            sc = await db.scalar(
                select(func.count(model.id)).where(model.moderation_status == s)
            )
            status_counts[s.value] += sc or 0

        # Get items with pagination
        query = query.order_by(model.created_at.desc())
        if content_type:  # Only paginate if filtering by type
            query = query.offset((page - 1) * page_size).limit(page_size)
        else:
            query = query.limit(page_size // len(content_types) + 1)

        result = await db.execute(query)
        for item in result.scalars():
            # Get tags for this item
            tags_query = (
                select(Tag.name)
                .join(ContentTag, ContentTag.tag_id == Tag.id)
                .where(
                    and_(
                        ContentTag.content_type == ct,
                        ContentTag.content_id == item.id
                    )
                )
            )
            tags_result = await db.execute(tags_query)
            tag_names = [t[0] for t in tags_result]

            # Get reviewer name if reviewed
            reviewer_name = None
            if item.reviewed_by_id:
                reviewer = await db.get(User, item.reviewed_by_id)
                if reviewer:
                    reviewer_name = reviewer.name or reviewer.email

            items.append(AdminContentItem(
                id=item.id,
                content_type=ct,
                title=get_title_from_content(item, ct),
                source=item.source.value if hasattr(item.source, 'value') else item.source,
                moderation_status=item.moderation_status,
                reviewed_by_name=reviewer_name,
                reviewed_at=item.reviewed_at,
                created_at=item.created_at,
                url=getattr(item, 'url', None) or getattr(item, 'website_url', None) or getattr(item, 'apply_url', None),
                tags=tag_names,
                categories=[],
            ))

    # Sort all items by created_at
    items.sort(key=lambda x: x.created_at, reverse=True)

    # Apply pagination to combined results
    if not content_type:
        items = items[(page - 1) * page_size:page * page_size]

    return AdminContentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        status_counts=status_counts,
    )


@router.get("/{content_type}/{content_id}")
async def get_content_item(
    content_type: str,
    content_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Get a specific content item."""
    if content_type not in CONTENT_MODELS:
        raise HTTPException(status_code=400, detail="Invalid content type")

    model = CONTENT_MODELS[content_type]
    item = await db.get(model, content_id)

    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    return item


@router.patch("/{content_type}/{content_id}/approve")
async def approve_content(
    content_type: str,
    content_id: int,
    request: Request,
    action: ModerationAction = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Approve a content item."""
    if content_type not in CONTENT_MODELS:
        raise HTTPException(status_code=400, detail="Invalid content type")

    model = CONTENT_MODELS[content_type]
    item = await db.get(model, content_id)

    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    previous_status = item.moderation_status.value

    # Update status
    item.moderation_status = ContentStatus.APPROVED
    item.reviewed_by_id = admin.id
    item.reviewed_at = datetime.utcnow()
    item.rejection_reason = None

    # Log moderation
    await log_moderation(
        db=db,
        content_type=content_type,
        content_id=content_id,
        action="approve",
        previous_status=previous_status,
        new_status=ContentStatus.APPROVED.value,
        reviewed_by=admin.id,
        notes=action.notes if action else None,
    )

    # Log audit
    await log_audit(
        db=db,
        admin_id=admin.id,
        action="approve_content",
        entity_type=content_type,
        entity_id=content_id,
        old_values={"status": previous_status},
        new_values={"status": ContentStatus.APPROVED.value, "title": get_title_from_content(item, content_type)},
        request=request,
    )

    await db.commit()
    return {"message": "Content approved", "id": content_id, "status": "approved"}


@router.patch("/{content_type}/{content_id}/reject")
async def reject_content(
    content_type: str,
    content_id: int,
    request: Request,
    action: ModerationAction,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Reject a content item."""
    if content_type not in CONTENT_MODELS:
        raise HTTPException(status_code=400, detail="Invalid content type")

    model = CONTENT_MODELS[content_type]
    item = await db.get(model, content_id)

    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    previous_status = item.moderation_status.value

    # Update status
    item.moderation_status = ContentStatus.REJECTED
    item.reviewed_by_id = admin.id
    item.reviewed_at = datetime.utcnow()
    item.rejection_reason = action.reason

    # Log moderation
    await log_moderation(
        db=db,
        content_type=content_type,
        content_id=content_id,
        action="reject",
        previous_status=previous_status,
        new_status=ContentStatus.REJECTED.value,
        reviewed_by=admin.id,
        reason=action.reason,
        notes=action.notes,
    )

    # Log audit
    await log_audit(
        db=db,
        admin_id=admin.id,
        action="reject_content",
        entity_type=content_type,
        entity_id=content_id,
        old_values={"status": previous_status},
        new_values={"status": ContentStatus.REJECTED.value, "reason": action.reason},
        request=request,
    )

    await db.commit()
    return {"message": "Content rejected", "id": content_id, "status": "rejected"}


@router.patch("/{content_type}/{content_id}/flag")
async def flag_content(
    content_type: str,
    content_id: int,
    request: Request,
    action: ModerationAction,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Flag a content item for review."""
    if content_type not in CONTENT_MODELS:
        raise HTTPException(status_code=400, detail="Invalid content type")

    model = CONTENT_MODELS[content_type]
    item = await db.get(model, content_id)

    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    previous_status = item.moderation_status.value

    # Update status
    item.moderation_status = ContentStatus.FLAGGED
    item.reviewed_by_id = admin.id
    item.reviewed_at = datetime.utcnow()

    # Log moderation
    await log_moderation(
        db=db,
        content_type=content_type,
        content_id=content_id,
        action="flag",
        previous_status=previous_status,
        new_status=ContentStatus.FLAGGED.value,
        reviewed_by=admin.id,
        reason=action.reason,
        notes=action.notes,
    )

    # Log audit
    await log_audit(
        db=db,
        admin_id=admin.id,
        action="flag_content",
        entity_type=content_type,
        entity_id=content_id,
        old_values={"status": previous_status},
        new_values={"status": ContentStatus.FLAGGED.value, "reason": action.reason},
        request=request,
    )

    await db.commit()
    return {"message": "Content flagged", "id": content_id, "status": "flagged"}


@router.patch("/{content_type}/{content_id}/archive")
async def archive_content(
    content_type: str,
    content_id: int,
    request: Request,
    action: ModerationAction = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Archive a content item."""
    if content_type not in CONTENT_MODELS:
        raise HTTPException(status_code=400, detail="Invalid content type")

    model = CONTENT_MODELS[content_type]
    item = await db.get(model, content_id)

    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    previous_status = item.moderation_status.value

    # Update status
    item.moderation_status = ContentStatus.ARCHIVED
    item.reviewed_by_id = admin.id
    item.reviewed_at = datetime.utcnow()

    # Log audit
    await log_audit(
        db=db,
        admin_id=admin.id,
        action="archive_content",
        entity_type=content_type,
        entity_id=content_id,
        old_values={"status": previous_status},
        new_values={"status": ContentStatus.ARCHIVED.value},
        request=request,
    )

    await db.commit()
    return {"message": "Content archived", "id": content_id, "status": "archived"}


@router.post("/bulk-action")
async def bulk_moderation_action(
    request: Request,
    bulk_request: BulkModerationRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Perform bulk moderation action on multiple items."""
    if bulk_request.content_type not in CONTENT_MODELS:
        raise HTTPException(status_code=400, detail="Invalid content type")

    model = CONTENT_MODELS[bulk_request.content_type]
    action_map = {
        "approve": ContentStatus.APPROVED,
        "reject": ContentStatus.REJECTED,
        "flag": ContentStatus.FLAGGED,
        "archive": ContentStatus.ARCHIVED,
    }

    if bulk_request.action not in action_map:
        raise HTTPException(status_code=400, detail="Invalid action")

    new_status = action_map[bulk_request.action]
    processed = []
    errors = []

    for content_id in bulk_request.content_ids:
        item = await db.get(model, content_id)
        if not item:
            errors.append({"id": content_id, "error": "Not found"})
            continue

        previous_status = item.moderation_status.value
        item.moderation_status = new_status
        item.reviewed_by_id = admin.id
        item.reviewed_at = datetime.utcnow()

        if bulk_request.action == "reject":
            item.rejection_reason = bulk_request.reason

        # Log moderation
        await log_moderation(
            db=db,
            content_type=bulk_request.content_type,
            content_id=content_id,
            action=bulk_request.action,
            previous_status=previous_status,
            new_status=new_status.value,
            reviewed_by=admin.id,
            reason=bulk_request.reason,
        )

        processed.append(content_id)

    # Log bulk audit
    await log_audit(
        db=db,
        admin_id=admin.id,
        action=f"bulk_{bulk_request.action}_content",
        entity_type=bulk_request.content_type,
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


@router.get("/{content_type}/{content_id}/history", response_model=List[ContentModerationResponse])
async def get_moderation_history(
    content_type: str,
    content_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Get moderation history for a content item."""
    query = (
        select(ContentModeration, User.name)
        .join(User, ContentModeration.reviewed_by == User.id)
        .where(
            and_(
                ContentModeration.content_type == content_type,
                ContentModeration.content_id == content_id
            )
        )
        .order_by(ContentModeration.created_at.desc())
    )
    result = await db.execute(query)

    history = []
    for moderation, reviewer_name in result:
        history.append(ContentModerationResponse(
            id=moderation.id,
            content_type=moderation.content_type,
            content_id=moderation.content_id,
            action=moderation.action,
            previous_status=moderation.previous_status,
            new_status=moderation.new_status,
            reviewed_by=moderation.reviewed_by,
            reviewer_name=reviewer_name,
            reason=moderation.reason,
            notes=moderation.notes,
            created_at=moderation.created_at,
        ))

    return history


@router.post("/{content_type}/{content_id}/tags")
async def add_tags_to_content(
    content_type: str,
    content_id: int,
    tag_ids: List[int],
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Add tags to a content item."""
    if content_type not in CONTENT_MODELS:
        raise HTTPException(status_code=400, detail="Invalid content type")

    model = CONTENT_MODELS[content_type]
    item = await db.get(model, content_id)

    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    added = []
    for tag_id in tag_ids:
        tag = await db.get(Tag, tag_id)
        if not tag:
            continue

        # Check if already exists
        existing = await db.scalar(
            select(ContentTag.id).where(
                and_(
                    ContentTag.tag_id == tag_id,
                    ContentTag.content_type == content_type,
                    ContentTag.content_id == content_id,
                )
            )
        )
        if existing:
            continue

        # Add tag
        content_tag = ContentTag(
            tag_id=tag_id,
            content_type=content_type,
            content_id=content_id,
        )
        db.add(content_tag)

        # Update usage count
        tag.usage_count += 1
        added.append(tag_id)

    if added:
        await log_audit(
            db=db,
            admin_id=admin.id,
            action="add_tags",
            entity_type=content_type,
            entity_id=content_id,
            new_values={"tag_ids": added},
            request=request,
        )

    await db.commit()
    return {"message": "Tags added", "added": added}


@router.delete("/{content_type}/{content_id}/tags/{tag_id}")
async def remove_tag_from_content(
    content_type: str,
    content_id: int,
    tag_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Remove a tag from a content item."""
    # Find the content tag
    query = select(ContentTag).where(
        and_(
            ContentTag.tag_id == tag_id,
            ContentTag.content_type == content_type,
            ContentTag.content_id == content_id,
        )
    )
    result = await db.execute(query)
    content_tag = result.scalar_one_or_none()

    if not content_tag:
        raise HTTPException(status_code=404, detail="Tag not found on content")

    # Update usage count
    tag = await db.get(Tag, tag_id)
    if tag and tag.usage_count > 0:
        tag.usage_count -= 1

    await db.delete(content_tag)

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="remove_tag",
        entity_type=content_type,
        entity_id=content_id,
        old_values={"tag_id": tag_id},
        request=request,
    )

    await db.commit()
    return {"message": "Tag removed"}
