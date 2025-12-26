"""Admin API sources management endpoints."""
import re
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import httpx
import feedparser

from app.db.database import get_db
from app.models.user import User
from app.models.admin import APISource, AuditLog
from app.core.deps import get_current_admin
from app.schemas.admin import (
    APISourceCreate,
    APISourceUpdate,
    APISourceResponse,
    APISourceListResponse,
    APISourceTestRequest,
    APISourceTestResponse,
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


@router.get("", response_model=APISourceListResponse)
async def list_sources(
    is_active: Optional[bool] = None,
    source_type: Optional[str] = Query(None, pattern=r"^(rss|api|scrape)$"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """List all API sources."""
    query = select(APISource)

    if is_active is not None:
        query = query.where(APISource.is_active == is_active)
    if source_type:
        query = query.where(APISource.source_type == source_type)

    query = query.order_by(APISource.name)
    result = await db.execute(query)

    sources = [APISourceResponse.model_validate(s) for s in result.scalars()]
    total = len(sources)

    return APISourceListResponse(items=sources, total=total)


@router.get("/{source_id}", response_model=APISourceResponse)
async def get_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get a specific API source."""
    source = await db.get(APISource, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="API source not found")
    return APISourceResponse.model_validate(source)


@router.post("", response_model=APISourceResponse)
async def create_source(
    source_data: APISourceCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Create a new API source."""
    # Create slug
    slug = create_slug(source_data.name)
    slug_exists = await db.scalar(select(APISource).where(APISource.slug == slug))
    if slug_exists:
        count = await db.scalar(select(func.count(APISource.id)).where(APISource.slug.like(f"{slug}%")))
        slug = f"{slug}-{count + 1}"

    source = APISource(
        name=source_data.name,
        slug=slug,
        source_type=source_data.source_type,
        url=source_data.url,
        is_active=source_data.is_active,
        requires_api_key=source_data.requires_api_key,
        auto_approve=source_data.auto_approve,
        fetch_frequency=source_data.fetch_frequency,
        config=source_data.config,
    )
    db.add(source)
    await db.flush()

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="create_api_source",
        entity_type="api_source",
        entity_id=source.id,
        new_values={"name": source.name, "url": source.url},
        request=request,
    )

    await db.commit()
    await db.refresh(source)
    return APISourceResponse.model_validate(source)


@router.put("/{source_id}", response_model=APISourceResponse)
async def update_source(
    source_id: int,
    source_data: APISourceUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Update an API source."""
    source = await db.get(APISource, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="API source not found")

    old_values = {"name": source.name, "url": source.url, "is_active": source.is_active}

    if source_data.name is not None:
        source.name = source_data.name
        source.slug = create_slug(source_data.name)
    if source_data.source_type is not None:
        source.source_type = source_data.source_type
    if source_data.url is not None:
        source.url = source_data.url
    if source_data.is_active is not None:
        source.is_active = source_data.is_active
    if source_data.requires_api_key is not None:
        source.requires_api_key = source_data.requires_api_key
    if source_data.auto_approve is not None:
        source.auto_approve = source_data.auto_approve
    if source_data.fetch_frequency is not None:
        source.fetch_frequency = source_data.fetch_frequency
    if source_data.config is not None:
        source.config = source_data.config

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="update_api_source",
        entity_type="api_source",
        entity_id=source_id,
        old_values=old_values,
        new_values={"name": source.name, "url": source.url, "is_active": source.is_active},
        request=request,
    )

    await db.commit()
    await db.refresh(source)
    return APISourceResponse.model_validate(source)


@router.delete("/{source_id}")
async def delete_source(
    source_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Delete an API source."""
    source = await db.get(APISource, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="API source not found")

    source_name = source.name
    await db.delete(source)

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="delete_api_source",
        entity_type="api_source",
        entity_id=source_id,
        old_values={"name": source_name},
        request=request,
    )

    await db.commit()
    return {"message": "API source deleted", "id": source_id}


@router.patch("/{source_id}/toggle")
async def toggle_source(
    source_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Toggle an API source active/inactive."""
    source = await db.get(APISource, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="API source not found")

    old_state = source.is_active
    source.is_active = not source.is_active

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="toggle_api_source",
        entity_type="api_source",
        entity_id=source_id,
        old_values={"is_active": old_state},
        new_values={"is_active": source.is_active},
        request=request,
    )

    await db.commit()
    return {"message": f"API source {'activated' if source.is_active else 'deactivated'}", "id": source_id, "is_active": source.is_active}


@router.post("/{source_id}/fetch")
async def manual_fetch(
    source_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Trigger a manual fetch from an API source."""
    source = await db.get(APISource, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="API source not found")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if source.source_type == "rss":
                response = await client.get(source.url)
                response.raise_for_status()
                feed = feedparser.parse(response.text)
                items_count = len(feed.entries)
            else:
                response = await client.get(source.url)
                response.raise_for_status()
                data = response.json()
                items_count = len(data) if isinstance(data, list) else 1

        # Update source status
        source.last_fetched_at = datetime.utcnow()
        source.last_success_at = datetime.utcnow()
        source.last_error = None
        source.error_count = 0
        source.items_fetched += items_count

        await log_audit(
            db=db,
            admin_id=admin.id,
            action="manual_fetch_api_source",
            entity_type="api_source",
            entity_id=source_id,
            new_values={"items_fetched": items_count},
            request=request,
        )

        await db.commit()
        return {
            "message": "Fetch successful",
            "id": source_id,
            "items_fetched": items_count,
        }

    except Exception as e:
        source.last_fetched_at = datetime.utcnow()
        source.last_error = str(e)
        source.error_count += 1
        await db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Fetch failed: {str(e)}"
        )


@router.patch("/{source_id}/reset-errors")
async def reset_source_errors(
    source_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Reset error count for an API source."""
    source = await db.get(APISource, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="API source not found")

    old_error_count = source.error_count
    source.error_count = 0
    source.last_error = None

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="reset_api_source_errors",
        entity_type="api_source",
        entity_id=source_id,
        old_values={"error_count": old_error_count},
        new_values={"error_count": 0},
        request=request,
    )

    await db.commit()
    return {"message": "Errors reset", "id": source_id}


@router.post("/test", response_model=APISourceTestResponse)
async def test_source(
    test_request: APISourceTestRequest,
    admin: User = Depends(get_current_admin),
):
    """Test an API source without saving it."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if test_request.source_type == "rss":
                response = await client.get(test_request.url)
                response.raise_for_status()
                feed = feedparser.parse(response.text)

                if feed.bozo and feed.bozo_exception:
                    return APISourceTestResponse(
                        success=False,
                        message="Invalid RSS feed",
                        error=str(feed.bozo_exception),
                    )

                sample_items = []
                for entry in feed.entries[:3]:
                    sample_items.append({
                        "title": entry.get("title", "No title"),
                        "link": entry.get("link", ""),
                        "published": str(entry.get("published", "")),
                    })

                return APISourceTestResponse(
                    success=True,
                    message=f"RSS feed valid. Found {len(feed.entries)} items.",
                    sample_items=sample_items,
                )

            else:  # API or scrape
                headers = {}
                if test_request.config and "headers" in test_request.config:
                    headers = test_request.config["headers"]

                response = await client.get(test_request.url, headers=headers)
                response.raise_for_status()

                try:
                    data = response.json()
                    if isinstance(data, list):
                        sample_items = data[:3]
                        count = len(data)
                    elif isinstance(data, dict):
                        # Try common patterns
                        for key in ["items", "results", "data", "entries"]:
                            if key in data and isinstance(data[key], list):
                                sample_items = data[key][:3]
                                count = len(data[key])
                                break
                        else:
                            sample_items = [data]
                            count = 1

                    return APISourceTestResponse(
                        success=True,
                        message=f"API responded successfully. Found {count} items.",
                        sample_items=sample_items,
                    )
                except Exception:
                    return APISourceTestResponse(
                        success=True,
                        message="URL accessible but response is not JSON.",
                        sample_items=[{"content_type": response.headers.get("content-type", "unknown")}],
                    )

    except httpx.TimeoutException:
        return APISourceTestResponse(
            success=False,
            message="Request timed out",
            error="Connection timed out after 30 seconds",
        )
    except httpx.HTTPStatusError as e:
        return APISourceTestResponse(
            success=False,
            message=f"HTTP error: {e.response.status_code}",
            error=str(e),
        )
    except Exception as e:
        return APISourceTestResponse(
            success=False,
            message="Connection failed",
            error=str(e),
        )


@router.get("/stats/summary")
async def get_sources_summary(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get summary statistics for all API sources."""
    total = await db.scalar(select(func.count(APISource.id)))
    active = await db.scalar(select(func.count(APISource.id)).where(APISource.is_active == True))
    with_errors = await db.scalar(
        select(func.count(APISource.id)).where(APISource.error_count > 0)
    )
    total_items = await db.scalar(select(func.sum(APISource.items_fetched)))

    # By type
    by_type = {}
    for source_type in ["rss", "api", "scrape"]:
        count = await db.scalar(
            select(func.count(APISource.id)).where(APISource.source_type == source_type)
        )
        by_type[source_type] = count or 0

    return {
        "total": total or 0,
        "active": active or 0,
        "inactive": (total or 0) - (active or 0),
        "with_errors": with_errors or 0,
        "total_items_fetched": total_items or 0,
        "by_type": by_type,
    }
