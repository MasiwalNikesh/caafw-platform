"""Learning resources API endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.models.learning import LearningResource, ResourceType
from app.schemas.learning import LearningResourceResponse, LearningListResponse

router = APIRouter()


@router.get("", response_model=LearningListResponse)
async def list_resources(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    source: Optional[str] = None,
    resource_type: Optional[str] = None,
    level: Optional[str] = None,
    is_free: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    is_beginner_friendly: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = Query(default="created_at", pattern="^(created_at|rating|enrollments)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List learning resources with filtering and pagination."""
    query = select(LearningResource).where(LearningResource.is_active == True)

    # Apply filters
    if source:
        query = query.where(LearningResource.source == source)
    if resource_type:
        query = query.where(LearningResource.resource_type == resource_type)
    if level:
        query = query.where(LearningResource.level == level)
    if is_free is not None:
        query = query.where(LearningResource.is_free == is_free)
    if is_featured is not None:
        query = query.where(LearningResource.is_featured == is_featured)
    if is_beginner_friendly is not None:
        query = query.where(LearningResource.is_beginner_friendly == is_beginner_friendly)
    if search:
        query = query.where(
            LearningResource.title.ilike(f"%{search}%") |
            LearningResource.description.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(LearningResource, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    resources = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return LearningListResponse(
        items=[LearningResourceResponse.model_validate(r) for r in resources],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get("/types", response_model=List[dict])
async def list_resource_types():
    """List available resource types."""
    return [{"value": t.value, "label": t.name.title()} for t in ResourceType]


@router.get("/{resource_id}", response_model=LearningResourceResponse)
async def get_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single learning resource by ID."""
    query = select(LearningResource).where(
        LearningResource.id == resource_id,
        LearningResource.is_active == True
    )
    result = await db.execute(query)
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    return LearningResourceResponse.model_validate(resource)
