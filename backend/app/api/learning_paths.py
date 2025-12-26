"""Learning paths API endpoints."""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.models.learning_path import LearningPath, UserLearningProgress
from app.models.learning import LearningResource
from app.models.user import User
from app.core.deps import get_current_user, get_current_user_optional
from app.schemas.learning_path import (
    LearningPathResponse,
    LearningPathDetailResponse,
    LearningPathListResponse,
    UserProgressResponse,
    UserProgressUpdate,
    StartPathResponse,
    RecommendationsResponse,
    PathRecommendation,
)
from app.schemas.learning import LearningResourceResponse

router = APIRouter()


@router.get("", response_model=LearningPathListResponse)
async def list_learning_paths(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    level: Optional[str] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = Query(default="created_at", pattern="^(created_at|title|duration_hours)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List learning paths with filtering and pagination."""
    query = select(LearningPath).where(LearningPath.is_active == True)

    # Apply filters
    if level:
        query = query.where(LearningPath.level == level)
    if is_featured is not None:
        query = query.where(LearningPath.is_featured == is_featured)
    if search:
        query = query.where(
            LearningPath.title.ilike(f"%{search}%") |
            LearningPath.description.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(LearningPath, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    paths = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size if total else 0

    items = []
    for path in paths:
        response = LearningPathResponse.model_validate(path)
        response.resource_count = len(path.resource_ids) if path.resource_ids else 0
        items.append(response)

    return LearningPathListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Get personalized learning path recommendations based on user level."""
    user_level = None

    if current_user and current_user.profile:
        user_level = current_user.profile.ai_level

    # Default level mappings for recommendations
    level_priority = {
        "novice": ["novice", "beginner"],
        "beginner": ["beginner", "novice", "intermediate"],
        "intermediate": ["intermediate", "beginner", "expert"],
        "expert": ["expert", "intermediate"],
    }

    target_levels = level_priority.get(user_level, ["novice", "beginner"])

    # Get featured paths first, then filter by level
    query = (
        select(LearningPath)
        .where(LearningPath.is_active == True)
        .order_by(LearningPath.is_featured.desc(), LearningPath.created_at.desc())
        .limit(10)
    )

    result = await db.execute(query)
    paths = result.scalars().all()

    recommendations = []
    for path in paths:
        # Calculate match score based on level alignment
        if path.level in target_levels:
            idx = target_levels.index(path.level)
            match_score = 1.0 - (idx * 0.2)  # 1.0, 0.8, 0.6, etc.
        else:
            match_score = 0.3

        # Generate reason
        if path.level == user_level:
            reason = f"Perfect match for your {user_level} level"
        elif path.is_featured:
            reason = "Featured learning path"
        elif path.level in target_levels:
            reason = f"Recommended for {path.level} level learners"
        else:
            reason = "Expand your skills"

        path_response = LearningPathResponse.model_validate(path)
        path_response.resource_count = len(path.resource_ids) if path.resource_ids else 0

        recommendations.append(PathRecommendation(
            path=path_response,
            reason=reason,
            match_score=match_score,
        ))

    # Sort by match score
    recommendations.sort(key=lambda x: x.match_score, reverse=True)

    return RecommendationsResponse(
        recommendations=recommendations[:5],
        user_level=user_level,
    )


@router.get("/my-progress", response_model=List[dict])
async def get_my_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all learning paths the current user has started with their progress."""
    query = (
        select(UserLearningProgress, LearningPath)
        .join(LearningPath, UserLearningProgress.path_id == LearningPath.id)
        .where(UserLearningProgress.user_id == current_user.id)
        .order_by(UserLearningProgress.last_activity_at.desc().nullslast())
    )

    result = await db.execute(query)
    rows = result.all()

    progress_list = []
    for progress, path in rows:
        path_response = LearningPathResponse.model_validate(path)
        path_response.resource_count = len(path.resource_ids) if path.resource_ids else 0

        progress_list.append({
            "path": path_response,
            "progress": UserProgressResponse.model_validate(progress),
        })

    return progress_list


@router.get("/{path_id}", response_model=LearningPathDetailResponse)
async def get_learning_path(
    path_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Get a learning path with full resource details and user progress."""
    query = select(LearningPath).where(
        LearningPath.id == path_id,
        LearningPath.is_active == True
    )
    result = await db.execute(query)
    path = result.scalar_one_or_none()

    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    # Get resources in order
    resources = []
    if path.resource_ids:
        for resource_id in path.resource_ids:
            resource_query = select(LearningResource).where(
                LearningResource.id == resource_id,
                LearningResource.is_active == True
            )
            resource_result = await db.execute(resource_query)
            resource = resource_result.scalar_one_or_none()
            if resource:
                resources.append(LearningResourceResponse.model_validate(resource))

    # Get user progress if authenticated
    user_progress = None
    if current_user:
        progress_query = select(UserLearningProgress).where(
            UserLearningProgress.user_id == current_user.id,
            UserLearningProgress.path_id == path_id
        )
        progress_result = await db.execute(progress_query)
        progress = progress_result.scalar_one_or_none()
        if progress:
            user_progress = UserProgressResponse.model_validate(progress)

    response = LearningPathDetailResponse.model_validate(path)
    response.resource_count = len(resources)
    response.resources = resources
    response.user_progress = user_progress

    return response


@router.post("/{path_id}/start", response_model=StartPathResponse)
async def start_learning_path(
    path_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a learning path for the current user."""
    # Check if path exists
    path_query = select(LearningPath).where(
        LearningPath.id == path_id,
        LearningPath.is_active == True
    )
    path_result = await db.execute(path_query)
    path = path_result.scalar_one_or_none()

    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    # Check if already started
    existing_query = select(UserLearningProgress).where(
        UserLearningProgress.user_id == current_user.id,
        UserLearningProgress.path_id == path_id
    )
    existing_result = await db.execute(existing_query)
    existing = existing_result.scalar_one_or_none()

    if existing:
        return StartPathResponse(
            message="Learning path already started",
            progress=UserProgressResponse.model_validate(existing),
        )

    # Create new progress
    first_resource_id = path.resource_ids[0] if path.resource_ids else None
    now = datetime.utcnow()

    progress = UserLearningProgress(
        user_id=current_user.id,
        path_id=path_id,
        completed_resource_ids=[],
        current_resource_id=first_resource_id,
        progress_percentage=0,
        started_at=now,
        last_activity_at=now,
    )

    db.add(progress)
    await db.commit()
    await db.refresh(progress)

    return StartPathResponse(
        message="Learning path started successfully",
        progress=UserProgressResponse.model_validate(progress),
    )


@router.patch("/{path_id}/progress", response_model=UserProgressResponse)
async def update_progress(
    path_id: int,
    update: UserProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update progress on a learning path."""
    # Get the path
    path_query = select(LearningPath).where(
        LearningPath.id == path_id,
        LearningPath.is_active == True
    )
    path_result = await db.execute(path_query)
    path = path_result.scalar_one_or_none()

    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    # Get existing progress
    progress_query = select(UserLearningProgress).where(
        UserLearningProgress.user_id == current_user.id,
        UserLearningProgress.path_id == path_id
    )
    progress_result = await db.execute(progress_query)
    progress = progress_result.scalar_one_or_none()

    if not progress:
        raise HTTPException(
            status_code=404,
            detail="Progress not found. Start the learning path first."
        )

    # Update fields
    now = datetime.utcnow()

    if update.completed_resource_ids is not None:
        progress.completed_resource_ids = update.completed_resource_ids

        # Calculate progress percentage
        total_resources = len(path.resource_ids) if path.resource_ids else 1
        completed_count = len(update.completed_resource_ids)
        progress.progress_percentage = min(100, int((completed_count / total_resources) * 100))

        # Check if completed
        if progress.progress_percentage == 100 and not progress.completed_at:
            progress.completed_at = now

    if update.current_resource_id is not None:
        progress.current_resource_id = update.current_resource_id

    progress.last_activity_at = now

    await db.commit()
    await db.refresh(progress)

    return UserProgressResponse.model_validate(progress)


@router.post("/{path_id}/complete-resource/{resource_id}", response_model=UserProgressResponse)
async def complete_resource(
    path_id: int,
    resource_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a specific resource as completed in a learning path."""
    # Get the path
    path_query = select(LearningPath).where(
        LearningPath.id == path_id,
        LearningPath.is_active == True
    )
    path_result = await db.execute(path_query)
    path = path_result.scalar_one_or_none()

    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    # Validate resource is in path
    if resource_id not in (path.resource_ids or []):
        raise HTTPException(
            status_code=400,
            detail="Resource is not part of this learning path"
        )

    # Get or create progress
    progress_query = select(UserLearningProgress).where(
        UserLearningProgress.user_id == current_user.id,
        UserLearningProgress.path_id == path_id
    )
    progress_result = await db.execute(progress_query)
    progress = progress_result.scalar_one_or_none()

    now = datetime.utcnow()

    if not progress:
        # Auto-start the path
        progress = UserLearningProgress(
            user_id=current_user.id,
            path_id=path_id,
            completed_resource_ids=[resource_id],
            current_resource_id=resource_id,
            progress_percentage=0,
            started_at=now,
            last_activity_at=now,
        )
        db.add(progress)
    else:
        # Add to completed if not already there
        completed = list(progress.completed_resource_ids or [])
        if resource_id not in completed:
            completed.append(resource_id)
            progress.completed_resource_ids = completed

    # Calculate progress percentage
    total_resources = len(path.resource_ids) if path.resource_ids else 1
    completed_count = len(progress.completed_resource_ids or [])
    progress.progress_percentage = min(100, int((completed_count / total_resources) * 100))

    # Update current resource to next incomplete
    if path.resource_ids:
        for rid in path.resource_ids:
            if rid not in (progress.completed_resource_ids or []):
                progress.current_resource_id = rid
                break
        else:
            # All complete
            progress.current_resource_id = None
            if not progress.completed_at:
                progress.completed_at = now

    progress.last_activity_at = now

    await db.commit()
    await db.refresh(progress)

    return UserProgressResponse.model_validate(progress)


@router.delete("/{path_id}/progress", status_code=status.HTTP_204_NO_CONTENT)
async def reset_progress(
    path_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reset progress on a learning path."""
    progress_query = select(UserLearningProgress).where(
        UserLearningProgress.user_id == current_user.id,
        UserLearningProgress.path_id == path_id
    )
    progress_result = await db.execute(progress_query)
    progress = progress_result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")

    await db.delete(progress)
    await db.commit()
