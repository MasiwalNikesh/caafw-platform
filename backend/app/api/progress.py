"""Content progress tracking API endpoints."""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.deps import get_db, get_current_user
from app.models import User, ContentProgress, ProgressStatus
from app.schemas.bookmark import ContentType

router = APIRouter()


# Schemas
class ProgressBase(BaseModel):
    content_type: ContentType
    content_id: int


class ProgressUpdate(BaseModel):
    status: Optional[str] = None
    progress_percentage: Optional[int] = None
    time_spent_delta: Optional[int] = None  # Add to existing time


class ProgressResponse(BaseModel):
    id: int
    user_id: int
    content_type: str
    content_id: int
    status: str
    progress_percentage: int
    started_at: Optional[datetime]
    last_accessed_at: Optional[datetime]
    completed_at: Optional[datetime]
    time_spent: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProgressListResponse(BaseModel):
    items: List[ProgressResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProgressStats(BaseModel):
    total_items: int
    completed_items: int
    in_progress_items: int
    total_time_spent: int  # in seconds


# Endpoints
@router.get("/progress", response_model=ProgressListResponse)
async def list_progress(
    content_type: Optional[ContentType] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's content progress."""
    query = select(ContentProgress).where(ContentProgress.user_id == current_user.id)
    
    if content_type:
        query = query.where(ContentProgress.content_type == content_type.value)
    
    if status:
        query = query.where(ContentProgress.status == status)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Order by last accessed
    query = query.order_by(ContentProgress.last_accessed_at.desc().nullslast())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return ProgressListResponse(
        items=[ProgressResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/progress/stats", response_model=ProgressStats)
async def get_progress_stats(
    content_type: Optional[ContentType] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get progress statistics for the user."""
    base_query = select(ContentProgress).where(ContentProgress.user_id == current_user.id)
    
    if content_type:
        base_query = base_query.where(ContentProgress.content_type == content_type.value)
    
    # Total items
    total_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total_items = total_result.scalar() or 0
    
    # Completed items
    completed_result = await db.execute(
        select(func.count()).where(
            ContentProgress.user_id == current_user.id,
            ContentProgress.status == ProgressStatus.COMPLETED.value,
        )
    )
    completed_items = completed_result.scalar() or 0
    
    # In progress items
    in_progress_result = await db.execute(
        select(func.count()).where(
            ContentProgress.user_id == current_user.id,
            ContentProgress.status == ProgressStatus.IN_PROGRESS.value,
        )
    )
    in_progress_items = in_progress_result.scalar() or 0
    
    # Total time spent
    time_result = await db.execute(
        select(func.sum(ContentProgress.time_spent)).where(
            ContentProgress.user_id == current_user.id,
        )
    )
    total_time_spent = time_result.scalar() or 0
    
    return ProgressStats(
        total_items=total_items,
        completed_items=completed_items,
        in_progress_items=in_progress_items,
        total_time_spent=total_time_spent,
    )


@router.get("/progress/check")
async def check_progress(
    content_type: ContentType,
    content_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check progress status for specific content."""
    result = await db.execute(
        select(ContentProgress).where(
            ContentProgress.user_id == current_user.id,
            ContentProgress.content_type == content_type.value,
            ContentProgress.content_id == content_id,
        )
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        return {
            "has_progress": False,
            "status": ProgressStatus.NOT_STARTED.value,
            "progress_percentage": 0,
        }
    
    return {
        "has_progress": True,
        "progress_id": progress.id,
        "status": progress.status,
        "progress_percentage": progress.progress_percentage,
        "last_accessed_at": progress.last_accessed_at,
    }


@router.post("/progress/start", response_model=ProgressResponse)
async def start_progress(
    data: ProgressBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start tracking progress on content."""
    # Check if already exists
    result = await db.execute(
        select(ContentProgress).where(
            ContentProgress.user_id == current_user.id,
            ContentProgress.content_type == data.content_type.value,
            ContentProgress.content_id == data.content_id,
        )
    )
    progress = result.scalar_one_or_none()
    
    now = datetime.utcnow()
    
    if progress:
        # Update existing
        progress.last_accessed_at = now
        if progress.status == ProgressStatus.NOT_STARTED.value:
            progress.status = ProgressStatus.IN_PROGRESS.value
            progress.started_at = now
    else:
        # Create new
        progress = ContentProgress(
            user_id=current_user.id,
            content_type=data.content_type.value,
            content_id=data.content_id,
            status=ProgressStatus.IN_PROGRESS.value,
            started_at=now,
            last_accessed_at=now,
        )
        db.add(progress)
    
    await db.commit()
    await db.refresh(progress)
    
    return ProgressResponse.model_validate(progress)


@router.patch("/progress/{progress_id}", response_model=ProgressResponse)
async def update_progress(
    progress_id: int,
    data: ProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update progress on content."""
    result = await db.execute(
        select(ContentProgress).where(
            ContentProgress.id == progress_id,
            ContentProgress.user_id == current_user.id,
        )
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")
    
    now = datetime.utcnow()
    progress.last_accessed_at = now
    
    if data.status:
        progress.status = data.status
        if data.status == ProgressStatus.COMPLETED.value and not progress.completed_at:
            progress.completed_at = now
            progress.progress_percentage = 100
    
    if data.progress_percentage is not None:
        progress.progress_percentage = min(100, max(0, data.progress_percentage))
        if progress.progress_percentage == 100:
            progress.status = ProgressStatus.COMPLETED.value
            if not progress.completed_at:
                progress.completed_at = now
    
    if data.time_spent_delta:
        progress.time_spent += data.time_spent_delta
    
    await db.commit()
    await db.refresh(progress)
    
    return ProgressResponse.model_validate(progress)


@router.post("/progress/complete")
async def mark_complete(
    data: ProgressBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark content as completed."""
    result = await db.execute(
        select(ContentProgress).where(
            ContentProgress.user_id == current_user.id,
            ContentProgress.content_type == data.content_type.value,
            ContentProgress.content_id == data.content_id,
        )
    )
    progress = result.scalar_one_or_none()
    
    now = datetime.utcnow()
    
    if progress:
        progress.status = ProgressStatus.COMPLETED.value
        progress.progress_percentage = 100
        progress.completed_at = now
        progress.last_accessed_at = now
    else:
        progress = ContentProgress(
            user_id=current_user.id,
            content_type=data.content_type.value,
            content_id=data.content_id,
            status=ProgressStatus.COMPLETED.value,
            progress_percentage=100,
            started_at=now,
            completed_at=now,
            last_accessed_at=now,
        )
        db.add(progress)
    
    await db.commit()
    
    return {"message": "Marked as complete"}


@router.get("/progress/continue", response_model=List[ProgressResponse])
async def get_continue_list(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get recently accessed in-progress items."""
    result = await db.execute(
        select(ContentProgress)
        .where(
            ContentProgress.user_id == current_user.id,
            ContentProgress.status == ProgressStatus.IN_PROGRESS.value,
        )
        .order_by(ContentProgress.last_accessed_at.desc())
        .limit(limit)
    )
    items = result.scalars().all()
    
    return [ProgressResponse.model_validate(item) for item in items]

