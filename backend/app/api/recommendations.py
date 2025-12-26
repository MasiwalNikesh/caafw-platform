"""Enhanced AI recommendation engine with personalization."""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.deps import get_db, get_current_user, get_current_user_optional
from app.models import (
    User,
    UserProfile,
    Bookmark,
    ContentProgress,
    Product,
    Job,
    LearningResource,
    LearningPath,
    Event,
    ResearchPaper,
)

router = APIRouter()


class RecommendationItem(BaseModel):
    content_type: str
    content_id: int
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    reason: str
    score: float
    metadata: Dict[str, Any] = {}


class RecommendationsResponse(BaseModel):
    user_level: Optional[str] = None
    recommendations: List[RecommendationItem]
    personalized: bool


# Level mapping for content difficulty
LEVEL_SCORES = {
    "novice": 1,
    "beginner": 2,
    "intermediate": 3,
    "expert": 4,
}


def get_level_score(level: Optional[str]) -> int:
    """Get numeric score for a level."""
    if not level:
        return 2  # Default to beginner
    return LEVEL_SCORES.get(level.lower(), 2)


async def get_user_interests(db: AsyncSession, user_id: int) -> List[str]:
    """Extract user interests from bookmarks and progress."""
    # Get bookmarked content types
    bookmark_result = await db.execute(
        select(Bookmark.content_type, func.count(Bookmark.id).label('count'))
        .where(Bookmark.user_id == user_id)
        .group_by(Bookmark.content_type)
        .order_by(desc('count'))
        .limit(5)
    )
    bookmark_types = [row[0] for row in bookmark_result.all()]
    
    # Get progress content types
    progress_result = await db.execute(
        select(ContentProgress.content_type, func.count(ContentProgress.id).label('count'))
        .where(ContentProgress.user_id == user_id)
        .group_by(ContentProgress.content_type)
        .order_by(desc('count'))
        .limit(5)
    )
    progress_types = [row[0] for row in progress_result.all()]
    
    # Combine and deduplicate
    interests = list(dict.fromkeys(bookmark_types + progress_types))
    return interests


async def get_learning_path_recommendations(
    db: AsyncSession,
    user_level: Optional[str],
    limit: int = 5,
) -> List[RecommendationItem]:
    """Get learning path recommendations based on user level."""
    level_score = get_level_score(user_level)
    
    # Get paths matching user level and adjacent levels
    query = select(LearningPath).where(LearningPath.is_active == True)
    
    result = await db.execute(query.order_by(desc(LearningPath.is_featured)).limit(20))
    paths = result.scalars().all()
    
    recommendations = []
    for path in paths:
        path_level_score = get_level_score(path.level)
        
        # Score based on level match (higher for exact match)
        level_diff = abs(path_level_score - level_score)
        if level_diff == 0:
            score = 1.0
            reason = f"Perfect match for your {user_level} level"
        elif level_diff == 1:
            if path_level_score > level_score:
                score = 0.8
                reason = "Great next step to advance your skills"
            else:
                score = 0.6
                reason = "Reinforce your foundational knowledge"
        else:
            score = 0.4
            reason = "Explore new learning opportunities"
        
        # Boost featured paths
        if path.is_featured:
            score = min(1.0, score + 0.1)
            reason = "Featured: " + reason
        
        recommendations.append(RecommendationItem(
            content_type="learning_path",
            content_id=path.id,
            title=path.title,
            description=path.description,
            reason=reason,
            score=score,
            metadata={
                "level": path.level,
                "resource_count": path.resource_count,
                "topics": path.topics or [],
            },
        ))
    
    # Sort by score and return top items
    recommendations.sort(key=lambda x: x.score, reverse=True)
    return recommendations[:limit]


async def get_product_recommendations(
    db: AsyncSession,
    interests: List[str],
    limit: int = 5,
) -> List[RecommendationItem]:
    """Get product recommendations."""
    # Get popular products
    result = await db.execute(
        select(Product)
        .where(Product.is_active == True)
        .order_by(desc(Product.upvotes))
        .limit(limit * 2)
    )
    products = result.scalars().all()
    
    recommendations = []
    for product in products:
        score = 0.7
        reason = "Popular in the community"
        
        # Boost based on pricing (free products more accessible)
        if product.pricing_type == "free":
            score += 0.1
            reason = "Free and popular tool"
        
        recommendations.append(RecommendationItem(
            content_type="product",
            content_id=product.id,
            title=product.name,
            description=product.tagline or product.description,
            url=product.website_url,
            image_url=product.logo_url,
            reason=reason,
            score=score,
            metadata={
                "pricing_type": product.pricing_type,
                "upvotes": product.upvotes,
                "tags": product.tags or [],
            },
        ))
    
    recommendations.sort(key=lambda x: x.score, reverse=True)
    return recommendations[:limit]


async def get_job_recommendations(
    db: AsyncSession,
    user_level: Optional[str],
    limit: int = 5,
) -> List[RecommendationItem]:
    """Get job recommendations based on experience level."""
    level_score = get_level_score(user_level)
    
    # Map user level to job experience levels
    experience_mapping = {
        1: ["entry", "junior", "internship"],
        2: ["entry", "junior", "mid"],
        3: ["mid", "senior"],
        4: ["senior", "lead", "principal", "staff"],
    }
    target_levels = experience_mapping.get(level_score, ["entry", "mid"])
    
    result = await db.execute(
        select(Job)
        .where(Job.is_active == True)
        .order_by(desc(Job.posted_at))
        .limit(limit * 3)
    )
    jobs = result.scalars().all()
    
    recommendations = []
    for job in jobs:
        score = 0.5
        reason = "Recent opportunity"
        
        # Check experience level match
        job_level = (job.experience_level or "").lower()
        if any(lvl in job_level for lvl in target_levels):
            score = 0.9
            reason = f"Matches your {user_level} experience level"
        
        # Boost remote jobs
        if job.is_remote:
            score = min(1.0, score + 0.1)
        
        recommendations.append(RecommendationItem(
            content_type="job",
            content_id=job.id,
            title=job.title,
            description=f"{job.company_name} - {job.location or 'Remote'}",
            url=job.apply_url,
            image_url=job.company_logo,
            reason=reason,
            score=score,
            metadata={
                "company": job.company_name,
                "is_remote": job.is_remote,
                "location": job.location,
            },
        ))
    
    recommendations.sort(key=lambda x: x.score, reverse=True)
    return recommendations[:limit]


async def get_event_recommendations(
    db: AsyncSession,
    limit: int = 3,
) -> List[RecommendationItem]:
    """Get upcoming event recommendations."""
    from datetime import datetime
    
    result = await db.execute(
        select(Event)
        .where(Event.is_active == True)
        .where(Event.starts_at >= datetime.utcnow())
        .order_by(Event.starts_at)
        .limit(limit)
    )
    events = result.scalars().all()
    
    recommendations = []
    for event in events:
        score = 0.7
        reason = "Upcoming event"
        
        if event.is_free:
            score = 0.9
            reason = "Free upcoming event"
        
        recommendations.append(RecommendationItem(
            content_type="event",
            content_id=event.id,
            title=event.title,
            description=event.short_description,
            url=event.registration_url or event.url,
            image_url=event.image_url,
            reason=reason,
            score=score,
            metadata={
                "starts_at": event.starts_at.isoformat() if event.starts_at else None,
                "is_online": event.is_online,
                "is_free": event.is_free,
            },
        ))
    
    return recommendations


@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    limit: int = Query(10, ge=1, le=50),
    content_types: Optional[str] = None,  # comma-separated list
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Get personalized recommendations for the user.
    
    If user is authenticated, recommendations are based on:
    - User's AI level from quiz
    - Bookmarked content patterns
    - Progress and learning history
    
    If not authenticated, returns popular/featured content.
    """
    user_level = None
    interests = []
    personalized = False
    
    if current_user:
        # Get user profile for level
        profile_result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == current_user.id)
        )
        profile = profile_result.scalar_one_or_none()
        if profile:
            user_level = profile.ai_level
        
        # Get user interests from activity
        interests = await get_user_interests(db, current_user.id)
        personalized = True
    
    # Parse content types filter
    types_filter = None
    if content_types:
        types_filter = [t.strip() for t in content_types.split(",")]
    
    # Gather recommendations from different sources
    all_recommendations = []
    
    # Learning paths (most important for learning platform)
    if not types_filter or "learning_path" in types_filter:
        paths = await get_learning_path_recommendations(db, user_level, limit=5)
        all_recommendations.extend(paths)
    
    # Products
    if not types_filter or "product" in types_filter:
        products = await get_product_recommendations(db, interests, limit=4)
        all_recommendations.extend(products)
    
    # Jobs
    if not types_filter or "job" in types_filter:
        jobs = await get_job_recommendations(db, user_level, limit=3)
        all_recommendations.extend(jobs)
    
    # Events
    if not types_filter or "event" in types_filter:
        events = await get_event_recommendations(db, limit=2)
        all_recommendations.extend(events)
    
    # Sort all by score and limit
    all_recommendations.sort(key=lambda x: x.score, reverse=True)
    
    return RecommendationsResponse(
        user_level=user_level,
        recommendations=all_recommendations[:limit],
        personalized=personalized,
    )


@router.get("/recommendations/for-you")
async def get_for_you_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a personalized 'For You' feed mixing different content types.
    Requires authentication for full personalization.
    """
    # Get user profile
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    user_level = profile.ai_level if profile else None
    
    # Get recommendations
    all_recs = []
    
    paths = await get_learning_path_recommendations(db, user_level, limit=6)
    products = await get_product_recommendations(db, [], limit=6)
    jobs = await get_job_recommendations(db, user_level, limit=4)
    events = await get_event_recommendations(db, limit=4)
    
    all_recs.extend(paths)
    all_recs.extend(products)
    all_recs.extend(jobs)
    all_recs.extend(events)
    
    # Shuffle to mix content types (while respecting scores)
    # Group by score ranges and interleave
    high_score = [r for r in all_recs if r.score >= 0.8]
    med_score = [r for r in all_recs if 0.5 <= r.score < 0.8]
    low_score = [r for r in all_recs if r.score < 0.5]
    
    # Interleave content types within each group
    def interleave_by_type(items: List[RecommendationItem]) -> List[RecommendationItem]:
        by_type: Dict[str, List[RecommendationItem]] = {}
        for item in items:
            if item.content_type not in by_type:
                by_type[item.content_type] = []
            by_type[item.content_type].append(item)
        
        result = []
        while any(by_type.values()):
            for content_type in list(by_type.keys()):
                if by_type[content_type]:
                    result.append(by_type[content_type].pop(0))
                if not by_type[content_type]:
                    del by_type[content_type]
        return result
    
    mixed = interleave_by_type(high_score) + interleave_by_type(med_score) + interleave_by_type(low_score)
    
    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    page_items = mixed[start:end]
    
    return {
        "items": page_items,
        "total": len(mixed),
        "page": page,
        "page_size": page_size,
        "total_pages": (len(mixed) + page_size - 1) // page_size,
        "user_level": user_level,
    }

